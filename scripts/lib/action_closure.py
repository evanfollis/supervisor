#!/usr/bin/env python3
"""Typed, machine-verifiable completion receipts for the action ledger.

The receipt is evidence about closure, not a prose assertion. Every lifecycle
dimension must be explicitly complete, not-applicable, or deferred with a
reason. Referenced paths and commits are checked before a visible done
transition can be published.
"""

from __future__ import annotations

import hashlib
import json
import os
import re
import stat
import subprocess
from datetime import datetime
from pathlib import Path
from typing import Any

SCHEMA_VERSION = 1
DIMENSIONS = (
    "code_landed",
    "verification_passed",
    "deployed",
    "state_projection_refreshed",
    "source_artifact_dispositioned",
)
STATUSES = {"complete", "not_applicable", "deferred"}
DEFAULT_ARCHIVE_ROOT = Path("/opt/workspace/runtime/.meta/handoff-archive")


class ClosureReceiptError(ValueError):
    pass


def _parse_iso(value: object, label: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ClosureReceiptError(f"{label} must be a non-empty ISO timestamp")
    try:
        datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError as exc:
        raise ClosureReceiptError(f"{label} is not a valid ISO timestamp") from exc
    return value


def _regular_owned_file(path: Path, label: str) -> None:
    try:
        info = os.lstat(path)
    except FileNotFoundError as exc:
        raise ClosureReceiptError(f"{label} does not exist: {path}") from exc
    if stat.S_ISLNK(info.st_mode) or not stat.S_ISREG(info.st_mode):
        raise ClosureReceiptError(f"{label} must be a regular non-symlink file: {path}")
    if info.st_uid != os.geteuid():
        raise ClosureReceiptError(f"{label} owner mismatch: {path}")
    if stat.S_IMODE(info.st_mode) & 0o022:
        raise ClosureReceiptError(f"{label} must not be group/world writable: {path}")


def _absolute_path(value: object, label: str) -> Path:
    if not isinstance(value, str) or not value:
        raise ClosureReceiptError(f"{label} must be a non-empty path")
    path = Path(value)
    if not path.is_absolute():
        raise ClosureReceiptError(f"{label} must be absolute: {value}")
    return path


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _required_hash(value: object, label: str) -> str:
    if not isinstance(value, str) or not re.fullmatch(r"[0-9a-f]{64}", value):
        raise ClosureReceiptError(f"{label} must be a lowercase SHA-256 digest")
    return value


def _validate_hashed_file(path_value: object, hash_value: object, label: str) -> Path:
    path = _absolute_path(path_value, f"{label}.path")
    _regular_owned_file(path, label)
    expected = _required_hash(hash_value, f"{label}.sha256")
    if expected != _sha256(path):
        raise ClosureReceiptError(f"{label} sha256 mismatch")
    return path


def _git(repository: Path, *args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["git", "-C", str(repository), *args],
        capture_output=True,
        text=True,
        timeout=20,
    )


def _validate_git_commit(section: dict[str, Any]) -> None:
    repository = _absolute_path(section.get("repository"), "code_landed.repository")
    if not repository.is_dir():
        raise ClosureReceiptError(f"code_landed.repository is not a directory: {repository}")
    commit = section.get("commit")
    if not isinstance(commit, str) or not re.fullmatch(r"[0-9a-f]{40}", commit):
        raise ClosureReceiptError("code_landed.commit must be a full 40-character lowercase SHA")
    remote_ref = section.get("remote_ref", "origin/main")
    if not isinstance(remote_ref, str) or not remote_ref.strip():
        raise ClosureReceiptError("code_landed.remote_ref must be non-empty")
    if _git(repository, "cat-file", "-e", f"{commit}^{{commit}}").returncode != 0:
        raise ClosureReceiptError(f"code_landed.commit is not present in {repository}: {commit}")
    if _git(repository, "rev-parse", "--verify", remote_ref).returncode != 0:
        raise ClosureReceiptError(f"code_landed.remote_ref is not present: {remote_ref}")
    if _git(repository, "merge-base", "--is-ancestor", commit, remote_ref).returncode != 0:
        raise ClosureReceiptError(
            f"code_landed.commit is not durable on {remote_ref}: {commit}"
        )


def _validate_evidence(items: object, label: str) -> None:
    if not isinstance(items, list) or not items:
        raise ClosureReceiptError(f"{label}.evidence must be a non-empty list")
    for index, item in enumerate(items):
        item_label = f"{label}.evidence[{index}]"
        if not isinstance(item, dict):
            raise ClosureReceiptError(f"{item_label} must be an object")
        kind = item.get("kind")
        if kind == "path":
            _validate_hashed_file(
                item.get("value"), item.get("sha256"), item_label
            )
        elif kind == "command":
            if not isinstance(item.get("command"), str) or not item["command"].strip():
                raise ClosureReceiptError(f"{item_label}.command must be non-empty")
            if item.get("exit_code") != 0:
                raise ClosureReceiptError(f"{item_label}.exit_code must be 0")
            _parse_iso(item.get("observed_at"), f"{item_label}.observed_at")
        elif kind == "service":
            if not isinstance(item.get("unit"), str) or not item["unit"].strip():
                raise ClosureReceiptError(f"{item_label}.unit must be non-empty")
            if item.get("result") not in {"active", "success"}:
                raise ClosureReceiptError(f"{item_label}.result must be active or success")
            _parse_iso(item.get("observed_at"), f"{item_label}.observed_at")
        elif kind == "url":
            value = item.get("value")
            if not isinstance(value, str) or not re.match(r"^https?://", value):
                raise ClosureReceiptError(f"{item_label}.value must be an HTTP(S) URL")
            status_code = item.get("status")
            if not isinstance(status_code, int) or not 200 <= status_code < 400:
                raise ClosureReceiptError(f"{item_label}.status must be 200..399")
            _parse_iso(item.get("observed_at"), f"{item_label}.observed_at")
        else:
            raise ClosureReceiptError(f"{item_label}.kind is unsupported: {kind!r}")
        if kind in {"command", "service", "url"}:
            _validate_hashed_file(
                item.get("transcript_path"),
                item.get("transcript_sha256"),
                f"{item_label}.transcript",
            )


def _validate_dimension_status(name: str, section: object) -> dict[str, Any]:
    if not isinstance(section, dict):
        raise ClosureReceiptError(f"{name} must be an object")
    status_value = section.get("status")
    if status_value not in STATUSES:
        raise ClosureReceiptError(f"{name}.status must be one of {sorted(STATUSES)}")
    if status_value != "complete":
        reason = section.get("reason")
        if not isinstance(reason, str) or not reason.strip():
            raise ClosureReceiptError(f"{name}.reason is required for {status_value}")
    return section


def _inside(path: Path, root: Path) -> bool:
    try:
        path.resolve(strict=False).relative_to(root.resolve(strict=False))
        return True
    except ValueError:
        return False


def validate_receipt(
    receipt_path: Path,
    *,
    action_id: str,
    record_source: str,
    source_root: Path,
    archive_root: Path = DEFAULT_ARCHIVE_ROOT,
) -> tuple[dict[str, Any], tuple[Path, Path] | None]:
    """Validate a receipt and return its payload plus an optional source move."""
    if not receipt_path.is_absolute():
        raise ClosureReceiptError("completion receipt path must be absolute")
    _regular_owned_file(receipt_path, "completion receipt")
    try:
        payload = json.loads(receipt_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise ClosureReceiptError("completion receipt is not valid JSON") from exc
    if not isinstance(payload, dict):
        raise ClosureReceiptError("completion receipt must be a JSON object")
    if payload.get("schema_version") != SCHEMA_VERSION:
        raise ClosureReceiptError(f"completion receipt schema_version must be {SCHEMA_VERSION}")
    if payload.get("action_id") != action_id:
        raise ClosureReceiptError("completion receipt action_id does not match the ledger action")
    _parse_iso(payload.get("completed_at"), "completed_at")

    sections = {
        name: _validate_dimension_status(name, payload.get(name))
        for name in DIMENSIONS
    }
    deferred = [name for name, section in sections.items() if section["status"] == "deferred"]
    if deferred:
        raise ClosureReceiptError(
            "completion cannot contain deferred dimensions: " + ", ".join(deferred)
        )
    if sections["code_landed"]["status"] == "complete":
        _validate_git_commit(sections["code_landed"])
    if sections["verification_passed"]["status"] == "complete":
        _validate_evidence(sections["verification_passed"].get("evidence"), "verification_passed")
    if sections["deployed"]["status"] == "complete":
        _validate_evidence(sections["deployed"].get("evidence"), "deployed")
    if sections["state_projection_refreshed"]["status"] == "complete":
        _validate_hashed_file(
            sections["state_projection_refreshed"].get("path"),
            sections["state_projection_refreshed"].get("sha256"),
            "state_projection_refreshed",
        )

    source_move = None
    disposition = sections["source_artifact_dispositioned"]
    if disposition["status"] == "complete":
        source = _absolute_path(
            disposition.get("source_path"), "source_artifact_dispositioned.source_path"
        )
        archive = _absolute_path(
            disposition.get("archive_path"), "source_artifact_dispositioned.archive_path"
        )
        if record_source:
            declared = Path(record_source)
            if not declared.is_absolute():
                declared = source_root / declared
            if source.resolve(strict=False) != declared.resolve(strict=False):
                raise ClosureReceiptError(
                    "source_artifact_dispositioned.source_path does not match action source"
                )
        if not _inside(archive, archive_root):
            raise ClosureReceiptError(
                f"source archive must stay under {archive_root}: {archive}"
            )
        expected_source_hash = _required_hash(
            disposition.get("sha256"), "source_artifact_dispositioned.sha256"
        )
        if source.exists():
            _regular_owned_file(source, "source artifact")
            if _sha256(source) != expected_source_hash:
                raise ClosureReceiptError("source artifact sha256 mismatch")
            if archive.exists():
                raise ClosureReceiptError(f"source archive already exists: {archive}")
            source_move = (source, archive)
        elif archive.exists():
            _regular_owned_file(archive, "archived source artifact")
            if _sha256(archive) != expected_source_hash:
                raise ClosureReceiptError("archived source artifact sha256 mismatch")
        else:
            raise ClosureReceiptError(
                "source artifact is absent from both source and declared archive"
            )

    return payload, source_move
