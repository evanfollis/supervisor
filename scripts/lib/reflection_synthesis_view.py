#!/usr/bin/env python3
"""Publish a proposal-free reflection projection for cross-project synthesis."""

from __future__ import annotations

import hashlib
import json
import os
import tempfile
from pathlib import Path


def atomic_write(path: Path, value: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, temporary = tempfile.mkstemp(prefix=f".{path.name}.", dir=path.parent)
    try:
        os.fchmod(fd, 0o600)
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


def build_view(reflection_text: str, evidence: dict, invocation_id: str) -> str:
    lines = reflection_text.splitlines()
    try:
        proposals = lines.index("### Proposals")
        questions = lines.index("### Questions for the human")
    except ValueError as error:
        raise ValueError("reflection projection requires Proposals and Questions sections") from error
    if questions <= proposals:
        raise ValueError("reflection sections are out of order")
    observations = [
        item for item in evidence.get("observations", [])
        if item.get("status") == "OBSERVATION-OBJECT-MATCHED"
    ]
    view = [
        "# Typed reflection evidence projection",
        "",
        "This projection contains only exact primary-object references selected by",
        "typed observations. No model-written observation, summary, principle, security",
        "claim, or proposal prose is synthesis input. Synthesis must inspect the objects",
        "and form its own interpretation.",
        "Object identity does not establish entailment or authorize action.",
        "",
        "### Observation-selected primary objects",
        "",
    ]
    if observations:
        for index, item in enumerate(observations, start=1):
            references = [
                str(value.get("reference")) for value in item.get("evidence", [])
                if value.get("matched") and value.get("reference")
            ]
            view.extend([
                f"- Evidence set {index}",
                "  - Primary objects: " + ", ".join(f"`{ref}`" for ref in references),
            ])
    else:
        view.append("No object-matched observations in this window.")
    view.extend([
        "",
        "### Reflection proposal telemetry (excluded from synthesis input)",
        "",
        "Reflection proposals are retained in the private raw artifact for empirical study,",
        "but are deliberately absent from this synthesis projection. Synthesis may reason",
        "from the selected primary objects above; it must form prescriptions independently.",
        "",
        f"- Proposal count: {int(evidence.get('proposal_count') or 0)}",
        (
            "- Primary-object-matched count: "
            f"{int(evidence.get('primary_object_matched_count') or 0)}"
        ),
        f"- Unverified count: {int(evidence.get('unverified_count') or 0)}",
        (
            "- Critical-security object-matched count: "
            f"{int(evidence.get('critical_security_object_matched_count') or 0)}"
        ),
        (
            "- Critical-security unverified count: "
            f"{int(evidence.get('unverified_security_count') or 0)}"
        ),
        f"- Invocation ID: `{invocation_id}`",
        "",
        "### Questions for the human",
        "",
        "None.",
    ])
    return "\n".join(view).rstrip() + "\n"


def publish(
    reflection: Path,
    evidence_path: Path,
    manifest_path: Path,
    output: Path,
    artifact_path: Path | None = None,
) -> dict:
    reflection_text = reflection.read_text(encoding="utf-8")
    evidence = json.loads(evidence_path.read_text(encoding="utf-8"))
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    value = build_view(reflection_text, evidence, str(manifest.get("session_id") or "unknown"))
    encoded = value.encode()
    atomic_write(output, encoded)
    return {
        "path": str(artifact_path or output),
        "bytes": len(encoded),
        "sha256": hashlib.sha256(encoded).hexdigest(),
        "proposal_content_included": False,
        "raw_narrative_content_included": False,
        "input_contract": "observation-selected-primary-objects-only-v1",
    }


def finalize_manifest(manifest_path: Path, published: Path) -> dict:
    encoded = published.read_bytes()
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    manifest["synthesis_projection"] = {
        "path": str(published),
        "bytes": len(encoded),
        "sha256": hashlib.sha256(encoded).hexdigest(),
        "proposal_content_included": False,
        "raw_narrative_content_included": False,
        "input_contract": "observation-selected-primary-objects-only-v1",
    }
    atomic_write(
        manifest_path,
        (json.dumps(manifest, indent=2, sort_keys=True) + "\n").encode(),
    )
    return manifest["synthesis_projection"]


def main() -> int:
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("--reflection", required=True, type=Path)
    parser.add_argument("--evidence", required=True, type=Path)
    parser.add_argument("--manifest", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--artifact-path", type=Path)
    parser.add_argument("--finalize-manifest", action="store_true")
    args = parser.parse_args()
    if args.finalize_manifest:
        result = finalize_manifest(args.manifest, args.output)
    else:
        result = publish(
            args.reflection, args.evidence, args.manifest, args.output,
            args.artifact_path,
        )
    print(json.dumps(result))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
