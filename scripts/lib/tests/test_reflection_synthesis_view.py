#!/usr/bin/env python3
"""Contract tests for proposal-free synthesis projections."""

import json
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import reflection_synthesis_view as MODULE  # noqa: E402


REFLECTION = """### Summary
Summary with a hidden recommendation to delete the worker.
### Principle adherence
Measured.
### Observations
- [OBSERVATION-OBJECT-MATCHED] Important observation with primary evidence.
- [CRITICAL-SECURITY-OBJECT-MATCHED] Security prose is separately quarantined.
### Proposals
- [PRIMARY-OBJECT-MATCHED] `danger.py` — Delete everything.
  - Primary evidence: `file:/tmp/danger#sha256=deadbeef`
### Questions for the human
None.
"""


def test_projection_preserves_observations_but_excludes_proposals():
    view = MODULE.build_view(
        REFLECTION,
        {
            "proposal_count": 1,
            "primary_object_matched_count": 1,
            "unverified_count": 0,
            "observations": [{
                "finding": "Important observation with primary evidence.",
                "status": "OBSERVATION-OBJECT-MATCHED",
                "evidence": [{"matched": True, "reference": "file:/tmp/proof#sha256=" + "a" * 64}],
            }],
        },
        "invocation-1",
    )
    assert "Important observation" not in view
    assert "file:/tmp/proof#sha256=" in view
    assert "Delete everything" not in view
    assert "hidden recommendation" not in view
    assert "Security prose" not in view
    assert "proposal_content_included" not in view
    assert "Invocation ID: `invocation-1`" in view


def test_publish_records_non_promotional_projection_in_manifest():
    with tempfile.TemporaryDirectory() as root_value:
        root = Path(root_value)
        reflection = root / "raw.md"
        evidence = root / "evidence.json"
        manifest = root / "manifest.json"
        output = root / "projection.md"
        reflection.write_text(REFLECTION)
        evidence.write_text(json.dumps({
            "proposal_count": 1, "primary_object_matched_count": 1,
            "unverified_count": 0, "observations": [],
        }))
        manifest.write_text(json.dumps({"session_id": "invocation-2"}))
        published = root / "published-projection.md"
        result = MODULE.publish(reflection, evidence, manifest, output, published)
        assert result["proposal_content_included"] is False
        assert result["input_contract"] == "observation-selected-primary-objects-only-v1"
        assert "synthesis_projection" not in json.loads(manifest.read_text())
        output.replace(published)
        MODULE.finalize_manifest(manifest, published)
        assert json.loads(manifest.read_text())["synthesis_projection"]["path"] == str(published)


TESTS = [
    test_projection_preserves_observations_but_excludes_proposals,
    test_publish_records_non_promotional_projection_in_manifest,
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
