#!/usr/bin/env python3
"""Contract tests for bounded reflection snapshots."""

import importlib.util
import subprocess
import tempfile
from datetime import datetime, timezone
from pathlib import Path

MODULE_PATH = Path(__file__).resolve().parents[1] / "reflection-snapshot.py"
SPEC = importlib.util.spec_from_file_location("reflection_snapshot", MODULE_PATH)
MODULE = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(MODULE)


def make_repo(root: Path) -> Path:
    repo = root / "repo"
    subprocess.run(["git", "init", "-b", "main", repo], check=True, capture_output=True)
    subprocess.run(["git", "-C", repo, "config", "user.email", "test@example.com"], check=True)
    subprocess.run(["git", "-C", repo, "config", "user.name", "Test"], check=True)
    (repo / "tracked.txt").write_text("primary\n")
    subprocess.run(["git", "-C", repo, "add", "."], check=True)
    subprocess.run(["git", "-C", repo, "commit", "-m", "primary"], check=True, capture_output=True)
    return repo


def test_snapshot_contains_exact_file_and_commit_witnesses():
    with tempfile.TemporaryDirectory() as root_value:
        root = Path(root_value)
        repo = make_repo(root)
        payload = MODULE.build_snapshot(
            "fixture", repo, root / "snapshot.json", [], None, None, 12,
            now=datetime.now(timezone.utc),
        )
        tracked = next(item for item in payload["objects"] if item["path"].endswith("tracked.txt"))
        assert tracked["witness"].startswith("file:")
        assert len(tracked["sha256"]) == 64
        assert payload["git"]["head_witness"].startswith(f"commit:{repo}@")
        assert payload["scope"]["ignored_project_paths_excluded"] is True


def test_symlink_is_recorded_as_skipped_not_followed():
    with tempfile.TemporaryDirectory() as root_value:
        root = Path(root_value)
        repo = make_repo(root)
        target = root / "outside"
        target.write_text("secret")
        link = repo / "link"
        link.symlink_to(target)
        payload = MODULE.build_snapshot(
            "fixture", repo, root / "snapshot.json", [link], None, None, 12,
        )
        assert any(item["path"] == str(link) for item in payload["skipped"])
        assert all(item["path"] != str(link) for item in payload["objects"])


def test_untracked_project_file_is_visible():
    with tempfile.TemporaryDirectory() as root_value:
        root = Path(root_value)
        repo = make_repo(root)
        (repo / "inflight.txt").write_text("ongoing work\n")
        payload = MODULE.build_snapshot(
            "fixture", repo, root / "snapshot.json", [], None, None, 12,
        )
        assert any(item["path"].endswith("inflight.txt") for item in payload["objects"])
        assert "inflight.txt" in payload["git"]["status"]


TESTS = [
    test_snapshot_contains_exact_file_and_commit_witnesses,
    test_symlink_is_recorded_as_skipped_not_followed,
    test_untracked_project_file_is_visible,
]


if __name__ == "__main__":
    failures = 0
    for test in TESTS:
        try:
            test()
            print(f"ok: {test.__name__}")
        except Exception as error:
            failures += 1
            print(f"FAIL: {test.__name__}: {error}")
    print(f"\n{len(TESTS) - failures}/{len(TESTS)} passed")
    raise SystemExit(1 if failures else 0)
