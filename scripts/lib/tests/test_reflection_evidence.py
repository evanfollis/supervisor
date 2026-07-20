#!/usr/bin/env python3
"""Contract tests for deterministic reflection primary-object witnesses."""

import hashlib
import importlib.util
import json
import subprocess
import tempfile
from pathlib import Path

MODULE_PATH = Path(__file__).resolve().parents[1] / "reflection-evidence.py"
SPEC = importlib.util.spec_from_file_location("reflection_evidence", MODULE_PATH)
MODULE = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(MODULE)


def test_exact_file_and_commit_witnesses_are_labeled_without_truth_overclaim():
    with tempfile.TemporaryDirectory() as root:
        root = Path(root)
        evidence = root / "evidence.log"
        evidence.write_text("primary object\n")
        digest = hashlib.sha256(evidence.read_bytes()).hexdigest()
        repository = root / "repo"
        subprocess.run(["git", "init", "-b", "main", repository], check=True, capture_output=True)
        subprocess.run(["git", "-C", repository, "config", "user.email", "test@example.com"], check=True)
        subprocess.run(["git", "-C", repository, "config", "user.name", "Test"], check=True)
        (repository / "proof").write_text("proof")
        subprocess.run(["git", "-C", repository, "add", "proof"], check=True)
        subprocess.run(["git", "-C", repository, "commit", "-m", "proof"], check=True, capture_output=True)
        commit = subprocess.run(
            ["git", "-C", repository, "rev-parse", "HEAD"],
            check=True, capture_output=True, text=True,
        ).stdout.strip()
        reflection = root / "reflection.md"
        reflection.write_text(
            "### Proposals\n"
            "- [PROPOSAL] `worker.py` — Fix the observed fault.\n"
            f"  - Primary evidence: `file:{evidence}#sha256={digest}`, "
            f"`commit:{repository}@{commit}`\n"
            "### Questions for the human\n"
        )
        payload = MODULE.witness(reflection, root / "sidecar.json")
        assert payload["primary_object_matched_count"] == 1
        assert "- [PRIMARY-OBJECT-MATCHED] `worker.py`" in reflection.read_text()
        assert "does not establish" in payload["attestation_scope"]


def test_missing_or_stale_witness_is_unverified():
    with tempfile.TemporaryDirectory() as root:
        root = Path(root)
        evidence = root / "evidence.log"
        evidence.write_text("changed\n")
        reflection = root / "reflection.md"
        reflection.write_text(
            "### Proposals\n"
            f"- [PROPOSAL] `worker.py` — Change it.\n"
            f"  - Primary evidence: `file:{evidence}#sha256={'0' * 64}`\n"
        )
        payload = MODULE.witness(reflection, root / "sidecar.json")
        assert payload["unverified_count"] == 1
        assert "- [UNVERIFIED] `worker.py`" in reflection.read_text()


def test_critical_security_observation_routes_only_on_exact_object_match():
    with tempfile.TemporaryDirectory() as root_value:
        root = Path(root_value)
        evidence = root / "vulnerable.conf"
        evidence.write_text("public = true\n")
        digest = hashlib.sha256(evidence.read_bytes()).hexdigest()
        reflection = root / "reflection.md"
        reflection.write_text(
            "### Observations\n"
            "- [CRITICAL-SECURITY] Public control plane is exposed.\n"
            f"  - Primary evidence: `file:{evidence}#sha256={digest}`\n"
            "  - Remaining uncertainty: Exposure has not been exercised.\n"
            "### Proposals\n"
            "No proposals in this window.\n"
        )
        payload = MODULE.witness(reflection, root / "sidecar.json")
        assert payload["critical_security_count"] == 1
        assert payload["critical_security_object_matched_count"] == 1
        assert payload["unverified_security_count"] == 0
        assert "[CRITICAL-SECURITY-OBJECT-MATCHED]" in reflection.read_text()


def test_stale_critical_security_witness_is_retained_but_not_routed():
    with tempfile.TemporaryDirectory() as root_value:
        root = Path(root_value)
        evidence = root / "service.conf"
        evidence.write_text("private = true\n")
        reflection = root / "reflection.md"
        reflection.write_text(
            "### Observations\n"
            "- [CRITICAL-SECURITY] Service may be public.\n"
            f"  - Primary evidence: `file:{evidence}#sha256={'0' * 64}`\n"
            "### Proposals\n"
            "No proposals in this window.\n"
        )
        payload = MODULE.witness(reflection, root / "sidecar.json")
        assert payload["critical_security_count"] == 1
        assert payload["critical_security_object_matched_count"] == 0
        assert payload["unverified_security_count"] == 1
        assert "[UNVERIFIED-SECURITY]" in reflection.read_text()


def test_typed_descriptive_observation_is_object_matched():
    with tempfile.TemporaryDirectory() as root_value:
        root = Path(root_value)
        evidence = root / "state.json"
        evidence.write_text('{"open": 3}\n')
        digest = hashlib.sha256(evidence.read_bytes()).hexdigest()
        reflection = root / "reflection.md"
        reflection.write_text(
            "### Observations\n"
            "- [OBSERVATION] The state file reports three open records.\n"
            f"  - Primary evidence: `file:{evidence}#sha256={digest}`\n"
            "### Proposals\nNo proposals in this window.\n"
        )
        payload = MODULE.witness(reflection, root / "sidecar.json")
        assert payload["observation_object_matched_count"] == 1
        assert "[OBSERVATION-OBJECT-MATCHED]" in reflection.read_text()


def test_prescriptive_observation_is_quarantined_from_synthesis_contract():
    with tempfile.TemporaryDirectory() as root_value:
        root = Path(root_value)
        evidence = root / "state.json"
        evidence.write_text('{"open": 3}\n')
        digest = hashlib.sha256(evidence.read_bytes()).hexdigest()
        reflection = root / "reflection.md"
        reflection.write_text(
            "### Observations\n"
            "- [OBSERVATION] The worker should update the state file.\n"
            f"  - Primary evidence: `file:{evidence}#sha256={digest}`\n"
            "### Proposals\nNo proposals in this window.\n"
        )
        payload = MODULE.witness(reflection, root / "sidecar.json")
        assert payload["unverified_observation_count"] == 1
        assert payload["observations"][0]["reason"].startswith("prescriptive")
        assert "[UNVERIFIED-OBSERVATION]" in reflection.read_text()


def test_unstructured_proposal_is_counted_unverified():
    with tempfile.TemporaryDirectory() as root:
        root = Path(root)
        reflection = root / "reflection.md"
        reflection.write_text("### Proposals\n- Change something important.\n")
        payload = MODULE.witness(reflection, root / "sidecar.json")
        assert payload["unverified_count"] == 1
        assert payload["proposals"][0]["reason"].startswith("proposal does not use")


def test_manifest_records_attested_publication_not_private_candidate():
    with tempfile.TemporaryDirectory() as root_value:
        root = Path(root_value)
        evidence = root / "evidence.log"
        evidence.write_text("primary\n")
        digest = hashlib.sha256(evidence.read_bytes()).hexdigest()
        candidate = root / "private-candidate.md"
        candidate.write_text(
            "### Proposals\n"
            "- [PROPOSAL] `worker.py` — Change it.\n"
            f"  - Primary evidence: `file:{evidence}#sha256={digest}`\n"
        )
        sidecar = root / "private-evidence.json"
        published = root / "published-reflection.md"
        published_sidecar = root / "published-reflection.evidence.json"
        manifest = root / "manifest.json"
        manifest.write_text(json.dumps({
            "reflection": {"path": str(candidate), "sha256": "pre-attestation"},
        }))
        payload = MODULE.witness(candidate, sidecar)
        assert "primary_object_attestation" not in json.loads(manifest.read_text())
        candidate.replace(published)
        sidecar.replace(published_sidecar)
        payload["reflection"] = str(published)
        published_sidecar.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")
        MODULE.update_invocation_manifest(
            manifest, published, published, published_sidecar,
            published_sidecar, payload,
        )
        value = json.loads(manifest.read_text())
        assert value["reflection"]["path"] == str(published)
        assert value["primary_object_attestation"]["path"] == str(published_sidecar)
        assert value["primary_object_attestation"]["primary_object_matched_count"] == 1
        assert value["pre_attestation_reflection"]["sha256"] == "pre-attestation"


TESTS = [
    test_critical_security_observation_routes_only_on_exact_object_match,
    test_exact_file_and_commit_witnesses_are_labeled_without_truth_overclaim,
    test_manifest_records_attested_publication_not_private_candidate,
    test_missing_or_stale_witness_is_unverified,
    test_prescriptive_observation_is_quarantined_from_synthesis_contract,
    test_stale_critical_security_witness_is_retained_but_not_routed,
    test_typed_descriptive_observation_is_object_matched,
    test_unstructured_proposal_is_counted_unverified,
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
