#!/usr/bin/env python3
"""Build a bounded, deterministic read manifest for one reflection window."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import stat
import subprocess
import tempfile
from datetime import datetime, timedelta, timezone
from pathlib import Path

MAX_FILES = 10_000
MAX_FILE_BYTES = 16 * 1024 * 1024
MAX_TOTAL_BYTES = 512 * 1024 * 1024


def read_and_hash(path: Path) -> tuple[str, int]:
    flags = os.O_RDONLY | getattr(os, "O_CLOEXEC", 0) | getattr(os, "O_NOFOLLOW", 0)
    fd = os.open(path, flags)
    try:
        info = os.fstat(fd)
        if not stat.S_ISREG(info.st_mode) or info.st_uid != os.geteuid():
            raise ValueError("not an owned regular file")
        if info.st_size > MAX_FILE_BYTES:
            raise ValueError(f"exceeds per-file limit {MAX_FILE_BYTES}")
        digest = hashlib.sha256()
        total = 0
        while True:
            chunk = os.read(fd, 1024 * 1024)
            if not chunk:
                break
            total += len(chunk)
            if total > MAX_FILE_BYTES:
                raise ValueError(f"exceeds per-file limit {MAX_FILE_BYTES}")
            digest.update(chunk)
        return digest.hexdigest(), total
    finally:
        os.close(fd)


def git(repo: Path, *args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["git", "-C", str(repo), *args], capture_output=True, text=True,
        timeout=60, check=False,
    )


def project_files(repo: Path) -> list[Path]:
    result = subprocess.run(
        ["git", "-C", str(repo), "ls-files", "-co", "--exclude-standard", "-z"],
        capture_output=True, timeout=60, check=False,
    )
    if result.returncode != 0:
        return []
    return [repo / os.fsdecode(value) for value in result.stdout.split(b"\0") if value]


def atomic_json(path: Path, value: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, temporary = tempfile.mkstemp(prefix=f".{path.name}.", dir=path.parent)
    try:
        os.fchmod(fd, 0o600)
        with os.fdopen(fd, "w", encoding="utf-8") as handle:
            json.dump(value, handle, indent=2, sort_keys=True)
            handle.write("\n")
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temporary, path)
    finally:
        try:
            os.unlink(temporary)
        except FileNotFoundError:
            pass


def path_identity(path: Path) -> dict[str, int] | None:
    """Return non-content identity for an object that cannot be snapshotted."""
    try:
        info = os.lstat(path)
    except OSError:
        return None
    return {
        "device": info.st_dev,
        "inode": info.st_ino,
        "mode": info.st_mode,
        "size": info.st_size,
        "mtime_ns": info.st_mtime_ns,
    }


def build_snapshot(
    project: str,
    repo: Path,
    output: Path,
    explicit_files: list[Path],
    session_dir: Path | None,
    prior_reflection_dir: Path | None,
    hours: int,
    now: datetime | None = None,
) -> dict:
    now = now or datetime.now(timezone.utc)
    cutoff = now - timedelta(hours=hours)
    candidates: dict[str, tuple[Path, str]] = {}
    for path in project_files(repo):
        candidates[str(path)] = (path, "project")
    for path in explicit_files:
        candidates[str(path)] = (path, "explicit")
    if session_dir and session_dir.is_dir():
        recent = sorted(
            session_dir.glob("*.jsonl"),
            key=lambda item: item.stat().st_mtime if item.exists() else 0,
            reverse=True,
        )
        for path in recent[:10]:
            try:
                modified = datetime.fromtimestamp(path.stat().st_mtime, timezone.utc)
            except OSError:
                continue
            if modified >= cutoff:
                candidates[str(path)] = (path, "session-transcript")
    if prior_reflection_dir and prior_reflection_dir.is_dir():
        for path in sorted(
            prior_reflection_dir.glob(f"{project}-reflection-*.md"), reverse=True
        )[:5]:
            candidates[str(path)] = (path, "prior-reflection")

    objects: list[dict] = []
    skipped: list[dict] = []
    total_bytes = 0
    for key in sorted(candidates):
        path, source = candidates[key]
        if len(objects) >= MAX_FILES:
            skipped.append({
                "path": key, "source": source,
                "reason": "file-count limit reached", "identity": path_identity(path),
            })
            continue
        try:
            digest, size = read_and_hash(path)
        except (OSError, ValueError) as error:
            skipped.append({
                "path": key, "source": source, "reason": str(error),
                "identity": path_identity(path),
            })
            continue
        if total_bytes + size > MAX_TOTAL_BYTES:
            skipped.append({
                "path": key, "source": source,
                "reason": "total-byte limit reached", "identity": path_identity(path),
            })
            continue
        total_bytes += size
        objects.append({
            "path": key,
            "sha256": digest,
            "bytes": size,
            "source": source,
            "witness": f"file:{key}#sha256={digest}",
        })

    log = git(repo, "log", f"--since={hours} hours ago", "--stat", "--oneline")
    status = git(repo, "status", "--short")
    head = git(repo, "rev-parse", "HEAD")
    payload = {
        "schema_version": 1,
        "project": project,
        "project_dir": str(repo),
        "generated_at": now.isoformat().replace("+00:00", "Z"),
        "window_hours": hours,
        "scope": {
            "max_files": MAX_FILES,
            "max_file_bytes": MAX_FILE_BYTES,
            "max_total_bytes": MAX_TOTAL_BYTES,
            "object_count": len(objects),
            "object_bytes": total_bytes,
            "skipped_count": len(skipped),
            "ignored_project_paths_excluded": True,
            "ignored_path_exception": (
                "ignored paths supplied as explicit files are included"
            ),
        },
        "git": {
            "head": head.stdout.strip() if head.returncode == 0 else "",
            "head_witness": (
                f"commit:{repo}@{head.stdout.strip()}" if head.returncode == 0 else ""
            ),
            "log": log.stdout,
            "log_error": log.stderr.strip() if log.returncode else "",
            "status": status.stdout,
            "status_error": status.stderr.strip() if status.returncode else "",
        },
        "objects": objects,
        "skipped": skipped,
    }
    atomic_json(output, payload)
    return payload


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--project", required=True)
    parser.add_argument("--project-dir", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--explicit-file", action="append", default=[], type=Path)
    parser.add_argument("--session-dir", type=Path)
    parser.add_argument("--prior-reflection-dir", type=Path)
    parser.add_argument("--hours", type=int, default=12)
    args = parser.parse_args()
    payload = build_snapshot(
        args.project, args.project_dir, args.output, args.explicit_file,
        args.session_dir, args.prior_reflection_dir, args.hours,
    )
    print(json.dumps(payload["scope"], sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
