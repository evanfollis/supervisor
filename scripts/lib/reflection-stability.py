#!/usr/bin/env python3
"""Detect project mutation between reflection snapshot and publication."""

from __future__ import annotations

import argparse
import importlib.util
import json
import os
import tempfile
from pathlib import Path

SNAPSHOT_MODULE_PATH = Path(__file__).with_name("reflection-snapshot.py")
SPEC = importlib.util.spec_from_file_location("reflection_snapshot_runtime", SNAPSHOT_MODULE_PATH)
SNAPSHOT = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(SNAPSHOT)


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


def check(snapshot_path: Path, repo: Path) -> dict:
    snapshot = json.loads(snapshot_path.read_text(encoding="utf-8"))
    expected_objects = {
        item["path"]: item for item in snapshot.get("objects", [])
        if item.get("source") == "project"
    }
    expected_skipped = {
        item["path"]: item for item in snapshot.get("skipped", [])
        if item.get("source") == "project"
    }
    expected_paths = set(expected_objects) | set(expected_skipped)
    current_paths = {str(path) for path in SNAPSHOT.project_files(repo)}
    changes: list[dict] = []
    for path in sorted(expected_paths - current_paths):
        changes.append({"path": path, "change": "missing"})
    for path in sorted(current_paths - expected_paths):
        changes.append({"path": path, "change": "added"})
    for path in sorted(set(expected_objects) & current_paths):
        try:
            digest, size = SNAPSHOT.read_and_hash(Path(path))
        except (OSError, ValueError) as error:
            changes.append({"path": path, "change": "unreadable", "detail": str(error)})
            continue
        expected = expected_objects[path]
        if digest != expected.get("sha256") or size != expected.get("bytes"):
            changes.append({"path": path, "change": "content_changed"})
    for path in sorted(set(expected_skipped) & current_paths):
        expected_identity = expected_skipped[path].get("identity")
        current_identity = SNAPSHOT.path_identity(Path(path))
        if not expected_identity or current_identity != expected_identity:
            changes.append({"path": path, "change": "skipped_object_changed"})

    current_head = SNAPSHOT.git(repo, "rev-parse", "HEAD")
    current_status = SNAPSHOT.git(repo, "status", "--short")
    expected_git = snapshot.get("git") or {}
    if current_head.stdout.strip() != expected_git.get("head", ""):
        changes.append({"path": str(repo), "change": "head_changed"})
    if current_status.stdout != expected_git.get("status", ""):
        changes.append({"path": str(repo), "change": "status_changed"})
    return {
        "schema_version": 1,
        "stable": not changes,
        "project_dir": str(repo),
        "coherence_scope": {
            "tracked_and_nonignored_untracked_project_files": True,
            "ignored_project_paths": "excluded unless explicitly snapshotted",
            "model_execution_write_controls": "Read/Glob/Grep or read-only sandbox",
        },
        "changes": changes,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--snapshot", required=True, type=Path)
    parser.add_argument("--project-dir", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()
    result = check(args.snapshot, args.project_dir)
    atomic_json(args.output, result)
    print(json.dumps({"stable": result["stable"], "change_count": len(result["changes"])}))
    return 0 if result["stable"] else 6


if __name__ == "__main__":
    raise SystemExit(main())
