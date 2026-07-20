#!/usr/bin/env python3
"""Contract tests for reflection-window stability checks."""

import importlib.util
import subprocess
import tempfile
from pathlib import Path

STABILITY_PATH = Path(__file__).resolve().parents[1] / "reflection-stability.py"
SNAPSHOT_PATH = Path(__file__).resolve().parents[1] / "reflection-snapshot.py"


def load(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


STABILITY = load(STABILITY_PATH, "reflection_stability")
SNAPSHOT = load(SNAPSHOT_PATH, "reflection_snapshot_test")


def make_repo(root: Path) -> Path:
    repo = root / "repo"
    subprocess.run(["git", "init", "-b", "main", repo], check=True, capture_output=True)
    subprocess.run(["git", "-C", repo, "config", "user.email", "test@example.com"], check=True)
    subprocess.run(["git", "-C", repo, "config", "user.name", "Test"], check=True)
    (repo / "tracked.txt").write_text("before\n")
    subprocess.run(["git", "-C", repo, "add", "."], check=True)
    subprocess.run(["git", "-C", repo, "commit", "-m", "before"], check=True, capture_output=True)
    return repo


def test_unchanged_project_is_stable():
    with tempfile.TemporaryDirectory() as root_value:
        root = Path(root_value)
        repo = make_repo(root)
        snapshot = root / "snapshot.json"
        SNAPSHOT.build_snapshot("fixture", repo, snapshot, [], None, None, 12)
        assert STABILITY.check(snapshot, repo)["stable"] is True


def test_content_change_is_detected_even_when_status_shape_is_unchanged():
    with tempfile.TemporaryDirectory() as root_value:
        root = Path(root_value)
        repo = make_repo(root)
        (repo / "tracked.txt").write_text("dirty-one\n")
        snapshot = root / "snapshot.json"
        SNAPSHOT.build_snapshot("fixture", repo, snapshot, [], None, None, 12)
        (repo / "tracked.txt").write_text("dirty-two\n")
        result = STABILITY.check(snapshot, repo)
        assert result["stable"] is False
        assert any(item["change"] == "content_changed" for item in result["changes"])


def test_added_file_is_detected():
    with tempfile.TemporaryDirectory() as root_value:
        root = Path(root_value)
        repo = make_repo(root)
        snapshot = root / "snapshot.json"
        SNAPSHOT.build_snapshot("fixture", repo, snapshot, [], None, None, 12)
        (repo / "new.txt").write_text("new\n")
        result = STABILITY.check(snapshot, repo)
        assert any(item["change"] == "added" for item in result["changes"])


def test_unchanged_skipped_symlink_does_not_look_new():
    with tempfile.TemporaryDirectory() as root_value:
        root = Path(root_value)
        repo = make_repo(root)
        (repo / "link").symlink_to("tracked.txt")
        subprocess.run(["git", "-C", repo, "add", "link"], check=True)
        subprocess.run(
            ["git", "-C", repo, "commit", "-m", "symlink"],
            check=True, capture_output=True,
        )
        snapshot = root / "snapshot.json"
        SNAPSHOT.build_snapshot("fixture", repo, snapshot, [], None, None, 12)
        result = STABILITY.check(snapshot, repo)
        assert result["stable"] is True


TESTS = [
    test_added_file_is_detected,
    test_content_change_is_detected_even_when_status_shape_is_unchanged,
    test_unchanged_project_is_stable,
    test_unchanged_skipped_symlink_does_not_look_new,
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
