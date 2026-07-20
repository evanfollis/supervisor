#!/usr/bin/env python3
"""Regression tests for the deterministic test-collection witness."""

import json
import subprocess
import sys
import tempfile
from pathlib import Path

WITNESS = str(Path(__file__).resolve().parents[1] / "verification-witness.py")


def _run(repo, *args):
    return subprocess.run(
        [sys.executable, WITNESS, str(repo), *args],
        capture_output=True,
        text=True,
    )


def _fixture(root):
    repo = Path(root)
    (repo / ".verification").mkdir()
    (repo / "tests").mkdir()
    (repo / "tests" / "test_sample.py").write_text(
        "def test_one():\n    assert True\n\n"
        "TESTS = [test_one]\n"
    )
    manifest = repo / ".verification" / "test-collection.json"
    manifest.write_text(json.dumps({
        "schema_version": 1,
        "collectors": [{
            "id": "unit",
            "mode": "python-explicit-tests",
            "roots": ["tests"],
            "include": ["test_*.py"],
            "files": ["placeholder"],
            "cases": ["placeholder"],
        }],
    }))
    subprocess.run(["git", "init", "-b", "main", str(repo)], check=True, capture_output=True)
    subprocess.run(["git", "-C", str(repo), "add", "."], check=True)
    observed = json.loads(_run(repo, "--observe").stdout)
    actual = observed["collectors"][0]
    declared = json.loads(manifest.read_text())
    for field in ("files", "cases"):
        declared["collectors"][0][field] = actual[field]
    manifest.write_text(json.dumps(declared))
    subprocess.run(["git", "-C", str(repo), "add", "."], check=True)
    return repo, manifest


def test_matching_inventory_passes():
    with tempfile.TemporaryDirectory() as root:
        repo, _ = _fixture(root)
        result = _run(repo)
        assert result.returncode == 0, result.stderr
        assert "1 file(s), 1 runner-declared case(s)" in result.stdout
        print("ok: declared test inventory passes")


def test_added_test_fails_until_manifest_is_reviewed():
    with tempfile.TemporaryDirectory() as root:
        repo, _ = _fixture(root)
        test_file = repo / "tests" / "test_sample.py"
        test_file.write_text(
            "def test_one():\n    assert True\n\n"
            "def test_two():\n    assert True\n\n"
            "TESTS = [test_one, test_two]\n"
        )
        result = _run(repo)
        assert result.returncode == 1
        assert "cases added" in result.stderr
        assert "--observe" in result.stderr
        print("ok: collection drift fails closed with observed-inventory guidance")


def test_wrong_discovery_root_cannot_validate_as_empty_green():
    with tempfile.TemporaryDirectory() as root:
        repo, manifest = _fixture(root)
        payload = json.loads(manifest.read_text())
        payload["collectors"][0]["roots"] = ["empty"]
        (repo / "empty").mkdir()
        manifest.write_text(json.dumps(payload))
        subprocess.run(["git", "-C", str(repo), "add", "."], check=True)
        result = _run(repo)
        assert result.returncode == 1
        assert "collected zero files" in result.stderr
        print("ok: wrong discovery root cannot pass as an empty green suite")


def test_orphan_test_function_is_rejected_before_manifest_comparison():
    with tempfile.TemporaryDirectory() as root:
        repo, _ = _fixture(root)
        test_file = repo / "tests" / "test_sample.py"
        test_file.write_text(
            test_file.read_text() + "\ndef test_orphan():\n    assert True\n"
        )
        result = _run(repo)
        assert result.returncode == 1
        assert "missing from TESTS" in result.stderr
        assert "test_orphan" in result.stderr
        print("ok: orphan test function cannot disappear outside the runner list")


TESTS = [
    test_added_test_fails_until_manifest_is_reviewed,
    test_matching_inventory_passes,
    test_orphan_test_function_is_rejected_before_manifest_comparison,
    test_wrong_discovery_root_cannot_validate_as_empty_green,
]


def main():
    failures = 0
    for test in TESTS:
        try:
            test()
        except AssertionError as exc:
            failures += 1
            print(f"FAIL: {test.__name__}: {exc}")
    print(f"\n{len(TESTS) - failures}/{len(TESTS)} passed")
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
