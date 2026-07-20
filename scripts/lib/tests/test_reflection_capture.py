#!/usr/bin/env python3
"""Contract tests for lossless, off-path reflection capture."""

import gzip
import importlib.util
import json
import sys
import tempfile
from pathlib import Path

MODULE_PATH = Path(__file__).resolve().parents[1] / "reflection-capture.py"
sys.path.insert(0, str(MODULE_PATH.parent))
SPEC = importlib.util.spec_from_file_location("reflection_capture", MODULE_PATH)
MODULE = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(MODULE)


def test_final_result_and_full_transcript_are_retained():
    with tempfile.TemporaryDirectory() as root_value:
        root = Path(root_value)
        session_id = "11111111-1111-4111-8111-111111111111"
        result = root / "result.json"
        result.write_text(json.dumps({
            "session_id": session_id,
            "is_error": False,
            "result": (
                "preamble\n### Summary\nSummary.\n### Principle adherence\nMeasured.\n"
                "### Observations\nObserved.\n### Proposals\nNo proposals in this window.\n"
                "### Questions for the human\nNone.\n"
            ),
            "usage": {"input_tokens": 10},
        }))
        transcript = root / "session.jsonl"
        transcript_bytes = b'{"type":"assistant","message":"complete"}\n'
        transcript.write_bytes(transcript_bytes)
        stderr = root / "stderr.log"
        stderr.write_text("")
        archive = root / "session.jsonl.gz"
        manifest_path = root / "manifest.json"
        reflection = root / "reflection.md"

        manifest = MODULE.finalize(
            result, reflection, transcript, archive, manifest_path, stderr,
            session_id, "anthropic", "sonnet", "medium",
        )

        assert reflection.read_text().startswith("### Summary\n")
        assert gzip.decompress(archive.read_bytes()) == transcript_bytes
        assert manifest["transcript"]["status"] == "archived"
        assert manifest["transcript"]["hot_path_cleared"] is True
        assert manifest["transcript"]["retained_raw_copy"] == ""
        assert not transcript.exists()
        assert manifest["normalization"]["preamble_lines_removed"] == 1
        assert json.loads(manifest_path.read_text())["session_id"] == session_id
        assert oct(reflection.stat().st_mode & 0o777) == "0o600"


def test_missing_transcript_does_not_block_reflection():
    with tempfile.TemporaryDirectory() as root_value:
        root = Path(root_value)
        session_id = "22222222-2222-4222-8222-222222222222"
        result = root / "result.json"
        result.write_text(json.dumps({
            "session_id": session_id,
            "is_error": False,
            "result": (
                "### Summary\nS.\n### Principle adherence\nP.\n### Observations\nO.\n"
                "### Proposals\nNo proposals in this window.\n"
                "### Questions for the human\nNone.\n"
            ),
        }))
        stderr = root / "stderr.log"
        stderr.write_text("diagnostic")
        manifest = MODULE.finalize(
            result, root / "reflection.md", root / "missing.jsonl",
            root / "archive.gz", root / "manifest.json", stderr,
            session_id, "anthropic", "sonnet", "medium",
        )
        assert manifest["transcript"]["status"] == "not_archived"
        assert (root / "reflection.md").is_file()


def test_error_envelope_never_becomes_a_reflection():
    with tempfile.TemporaryDirectory() as root_value:
        root = Path(root_value)
        result = root / "result.json"
        result.write_text(json.dumps({"is_error": True, "result": "partial"}))
        (root / "stderr.log").write_text("")
        try:
            MODULE.finalize(
                result, root / "reflection.md", root / "missing.jsonl",
                root / "archive.gz", root / "manifest.json", root / "stderr.log",
                "33333333-3333-4333-8333-333333333333",
                "anthropic", "sonnet", "medium",
            )
        except ValueError as error:
            assert "is_error=true" in str(error)
        else:
            raise AssertionError("error envelope was accepted")


TESTS = [
    test_error_envelope_never_becomes_a_reflection,
    test_final_result_and_full_transcript_are_retained,
    test_missing_transcript_does_not_block_reflection,
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
