#!/usr/bin/env python3
"""Finalize a reflection while retaining its complete invocation evidence."""

from __future__ import annotations

import argparse
import gzip
import hashlib
import json
import os
import stat
import tempfile
from datetime import datetime, timezone
from pathlib import Path

from reflection_document import normalize_with_metadata

MAX_RESULT_BYTES = 4 * 1024 * 1024
COPY_BUFFER_BYTES = 1024 * 1024


def read_owned_regular(path: Path, limit: int | None = None) -> bytes:
    flags = os.O_RDONLY | getattr(os, "O_CLOEXEC", 0) | getattr(os, "O_NOFOLLOW", 0)
    fd = os.open(path, flags)
    try:
        info = os.fstat(fd)
        if not stat.S_ISREG(info.st_mode) or info.st_uid != os.geteuid():
            raise ValueError(f"unsafe capture source: {path}")
        if limit is not None and info.st_size > limit:
            raise ValueError(f"capture source exceeds {limit} bytes: {path}")
        chunks: list[bytes] = []
        total = 0
        while True:
            chunk = os.read(fd, COPY_BUFFER_BYTES)
            if not chunk:
                break
            total += len(chunk)
            if limit is not None and total > limit:
                raise ValueError(f"capture source exceeds {limit} bytes: {path}")
            chunks.append(chunk)
        return b"".join(chunks)
    finally:
        os.close(fd)


def atomic_write(path: Path, value: bytes, mode: int = 0o600) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, temporary = tempfile.mkstemp(prefix=f".{path.name}.", dir=path.parent)
    try:
        os.fchmod(fd, mode)
        with os.fdopen(fd, "wb") as handle:
            handle.write(value)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temporary, path)
    finally:
        try:
            os.unlink(temporary)
        except FileNotFoundError:
            pass


def gzip_owned_regular(source: Path, destination: Path) -> dict[str, object]:
    flags = os.O_RDONLY | getattr(os, "O_CLOEXEC", 0) | getattr(os, "O_NOFOLLOW", 0)
    source_fd = os.open(source, flags)
    temporary = ""
    try:
        info = os.fstat(source_fd)
        if not stat.S_ISREG(info.st_mode) or info.st_uid != os.geteuid():
            raise ValueError(f"unsafe transcript source: {source}")
        destination.parent.mkdir(parents=True, exist_ok=True)
        output_fd, temporary = tempfile.mkstemp(
            prefix=f".{destination.name}.", dir=destination.parent
        )
        os.fchmod(output_fd, 0o600)
        source_hash = hashlib.sha256()
        source_bytes = 0
        with os.fdopen(output_fd, "wb") as raw_output:
            with gzip.GzipFile(fileobj=raw_output, mode="wb", mtime=0) as compressed:
                while True:
                    chunk = os.read(source_fd, COPY_BUFFER_BYTES)
                    if not chunk:
                        break
                    source_hash.update(chunk)
                    source_bytes += len(chunk)
                    compressed.write(chunk)
            raw_output.flush()
            os.fsync(raw_output.fileno())
        os.replace(temporary, destination)
        temporary = ""
        archive = read_owned_regular(destination)
        hot_path_cleared = False
        hot_path_cleanup_error = ""
        retained_raw_copy = destination.with_name("transcript.source-retained.jsonl")
        try:
            os.replace(source, retained_raw_copy)
            hot_path_cleared = True
            try:
                os.unlink(retained_raw_copy)
                retained_raw_copy_value = ""
            except OSError:
                retained_raw_copy_value = str(retained_raw_copy)
        except OSError as relocation_error:
            try:
                os.unlink(source)
                hot_path_cleared = True
                retained_raw_copy_value = ""
            except OSError as unlink_error:
                retained_raw_copy_value = ""
                hot_path_cleanup_error = (
                    f"relocation failed: {relocation_error}; "
                    f"unlink failed: {unlink_error}"
                )
        return {
            "status": (
                "archived" if hot_path_cleared
                else "archived_source_retained_hot_path"
            ),
            "source": str(source),
            "source_bytes": source_bytes,
            "source_sha256": source_hash.hexdigest(),
            "archive": str(destination),
            "archive_bytes": len(archive),
            "archive_sha256": hashlib.sha256(archive).hexdigest(),
            "compression": "gzip",
            "hot_path_cleared": hot_path_cleared,
            "hot_path_cleanup_error": hot_path_cleanup_error,
            "retained_raw_copy": retained_raw_copy_value,
        }
    finally:
        os.close(source_fd)
        if temporary:
            try:
                os.unlink(temporary)
            except FileNotFoundError:
                pass


def finalize(
    result_path: Path,
    reflection_path: Path,
    transcript_source: Path,
    transcript_archive: Path,
    manifest_path: Path,
    stderr_path: Path,
    session_id: str,
    provider: str,
    model: str,
    effort: str,
) -> dict[str, object]:
    result_bytes = read_owned_regular(result_path, MAX_RESULT_BYTES)
    response = json.loads(result_bytes)
    if response.get("is_error"):
        raise ValueError("model result reports is_error=true")
    result = response.get("result")
    if not isinstance(result, str) or not result.strip():
        raise ValueError("model result contains no non-empty result text")
    response_session = response.get("session_id")
    if response_session and response_session != session_id:
        raise ValueError("model result session_id does not match requested session")

    normalized, normalization = normalize_with_metadata(result)
    reflection_bytes = normalized.encode()
    atomic_write(reflection_path, reflection_bytes)

    try:
        transcript = gzip_owned_regular(transcript_source, transcript_archive)
    except (OSError, ValueError) as error:
        transcript = {
            "status": "not_archived",
            "source": str(transcript_source),
            "error": str(error),
        }

    stderr_bytes = b""
    stderr_error = ""
    try:
        stderr_bytes = read_owned_regular(stderr_path)
    except (OSError, ValueError) as error:
        stderr_error = str(error)

    manifest = {
        "schema_version": 1,
        "captured_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "session_id": session_id,
        "provider": response.get("provider") or provider,
        "model": response.get("model") or model,
        "effort": response.get("effort") or effort,
        "provider_session_id": response.get("provider_session_id", ""),
        "reflection": {
            "path": str(reflection_path),
            "bytes": len(reflection_bytes),
            "sha256": hashlib.sha256(reflection_bytes).hexdigest(),
        },
        "result_envelope": {
            "path": str(result_path),
            "bytes": len(result_bytes),
            "sha256": hashlib.sha256(result_bytes).hexdigest(),
        },
        "stderr": {
            "path": str(stderr_path),
            "bytes": len(stderr_bytes),
            "sha256": hashlib.sha256(stderr_bytes).hexdigest(),
            "read_error": stderr_error,
        },
        "transcript": transcript,
        "usage": response.get("usage", {}),
        "cost_usd": response.get("total_cost_usd"),
        "duration_ms": response.get("duration_ms"),
        "num_turns": response.get("num_turns"),
        "normalization": normalization,
    }
    atomic_write(manifest_path, (json.dumps(manifest, indent=2, sort_keys=True) + "\n").encode())
    return manifest


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--result", required=True, type=Path)
    parser.add_argument("--reflection", required=True, type=Path)
    parser.add_argument("--transcript-source", required=True, type=Path)
    parser.add_argument("--transcript-archive", required=True, type=Path)
    parser.add_argument("--manifest", required=True, type=Path)
    parser.add_argument("--stderr", required=True, type=Path)
    parser.add_argument("--session-id", required=True)
    parser.add_argument("--provider", required=True)
    parser.add_argument("--model", required=True)
    parser.add_argument("--effort", required=True)
    args = parser.parse_args()
    manifest = finalize(
        args.result,
        args.reflection,
        args.transcript_source,
        args.transcript_archive,
        args.manifest,
        args.stderr,
        args.session_id,
        args.provider,
        args.model,
        args.effort,
    )
    print(json.dumps({
        "session_id": manifest["session_id"],
        "transcript_status": manifest["transcript"]["status"],
    }, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
