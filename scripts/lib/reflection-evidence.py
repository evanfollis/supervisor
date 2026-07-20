#!/usr/bin/env python3
"""Attest that reflection proposals cite intact primary objects.

The attestation is deliberately narrower than a truth verdict: matching bytes
prove that the cited object was identified exactly, not that it entails the
proposal.  The synthesis/decision layer remains responsible for that judgment.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import stat
import subprocess
import tempfile
from datetime import datetime, timezone
from pathlib import Path

PROPOSAL = re.compile(
    r"^- \[(?:PROPOSAL|PRIMARY-OBJECT-MATCHED|UNVERIFIED)\] `([^`]+)` — (.+)$"
)
SECURITY_OBSERVATION = re.compile(
    r"^- \[(?:CRITICAL-SECURITY|CRITICAL-SECURITY-OBJECT-MATCHED|UNVERIFIED-SECURITY)\] (.+)$"
)
OBSERVATION = re.compile(
    r"^- \[(?:OBSERVATION|OBSERVATION-OBJECT-MATCHED|UNVERIFIED-OBSERVATION)\] (.+)$"
)
EVIDENCE_LINE = re.compile(r"^  - Primary evidence:\s*(.+)$")
TOKEN = re.compile(r"`([^`]+)`")
PRESCRIPTIVE_LANGUAGE = re.compile(
    r"\b(?:add|change|create|delete|fix|implement|must|propose|recommend|"
    r"refactor|remove|replace|should|update)\b",
    re.IGNORECASE,
)
MAX_PRIMARY_OBJECT_BYTES = 16 * 1024 * 1024
MAX_REFLECTION_BYTES = 2 * 1024 * 1024


def digest_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def read_regular_file(path: Path, limit: int) -> bytes:
    """Read an owned regular file from one stable descriptor.

    O_NOFOLLOW plus descriptor-based inspection closes the lstat/read race in
    which a path could be replaced by a symlink between validation and use.
    """
    flags = os.O_RDONLY | getattr(os, "O_CLOEXEC", 0) | getattr(os, "O_NOFOLLOW", 0)
    fd = os.open(path, flags)
    try:
        info = os.fstat(fd)
        if not stat.S_ISREG(info.st_mode):
            raise ValueError("not a regular file")
        if info.st_uid != os.geteuid():
            raise ValueError("owner mismatch")
        if info.st_size > limit:
            raise ValueError(f"file exceeds {limit}-byte witness limit")
        chunks: list[bytes] = []
        remaining = limit + 1
        while remaining:
            chunk = os.read(fd, min(1024 * 1024, remaining))
            if not chunk:
                break
            chunks.append(chunk)
            remaining -= len(chunk)
        value = b"".join(chunks)
        if len(value) > limit:
            raise ValueError(f"file exceeds {limit}-byte witness limit")
        return value
    finally:
        os.close(fd)


def atomic_write(path: Path, value: bytes, mode: int = 0o600) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, temporary = tempfile.mkstemp(prefix=f".{path.name}.", dir=path.parent)
    try:
        os.fchmod(fd, mode)
        with os.fdopen(fd, "wb") as handle:
            handle.write(value)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temporary, path)
        directory_fd = os.open(path.parent, os.O_RDONLY | getattr(os, "O_DIRECTORY", 0))
        try:
            os.fsync(directory_fd)
        finally:
            os.close(directory_fd)
    finally:
        try:
            os.unlink(temporary)
        except FileNotFoundError:
            pass


def verify_reference(reference: str) -> dict[str, object]:
    result: dict[str, object] = {"reference": reference, "matched": False}
    try:
        if reference.startswith("file:"):
            match = re.fullmatch(r"file:(/.+)#sha256=([0-9a-f]{64})", reference)
            if not match:
                raise ValueError("invalid file witness syntax")
            path = Path(match.group(1))
            observed = digest_bytes(read_regular_file(path, MAX_PRIMARY_OBJECT_BYTES))
            result.update(path=str(path), expected_sha256=match.group(2), observed_sha256=observed)
            if observed != match.group(2):
                raise ValueError("file hash mismatch")
        elif reference.startswith("line:"):
            match = re.fullmatch(
                r"line:(/.+)#L([1-9][0-9]*)#sha256=([0-9a-f]{64})", reference
            )
            if not match:
                raise ValueError("invalid line witness syntax")
            path = Path(match.group(1))
            line_number = int(match.group(2))
            lines = read_regular_file(path, MAX_PRIMARY_OBJECT_BYTES).splitlines()
            if line_number > len(lines):
                raise ValueError("line witness is out of range")
            observed = digest_bytes(lines[line_number - 1])
            result.update(
                path=str(path), line=line_number,
                expected_sha256=match.group(3), observed_sha256=observed,
            )
            if observed != match.group(3):
                raise ValueError("line hash mismatch")
        elif reference.startswith("commit:"):
            match = re.fullmatch(r"commit:(/.+)@([0-9a-f]{40})", reference)
            if not match:
                raise ValueError("invalid commit witness syntax")
            repository = Path(match.group(1))
            commit = match.group(2)
            repository_info = os.lstat(repository)
            if stat.S_ISLNK(repository_info.st_mode) or not stat.S_ISDIR(repository_info.st_mode):
                raise ValueError("repository does not exist")
            if repository_info.st_uid != os.geteuid():
                raise ValueError("repository owner mismatch")
            check = subprocess.run(
                ["git", "-C", str(repository), "cat-file", "-e", f"{commit}^{{commit}}"],
                capture_output=True, timeout=20,
            )
            if check.returncode != 0:
                raise ValueError("commit does not exist in repository")
            result.update(repository=str(repository), commit=commit)
        else:
            raise ValueError("unsupported witness type")
        result["matched"] = True
    except (OSError, ValueError, subprocess.SubprocessError) as error:
        result["error"] = str(error)
    return result


def witness(
    reflection: Path, sidecar: Path, artifact_path: Path | None = None
) -> dict[str, object]:
    reflection_bytes = read_regular_file(reflection, MAX_REFLECTION_BYTES)
    lines = reflection_bytes.decode("utf-8").splitlines()
    in_proposals = False
    in_observations = False
    proposals: list[dict[str, object]] = []
    observations: list[dict[str, object]] = []
    security_findings: list[dict[str, object]] = []
    unstructured: list[dict[str, object]] = []
    for index, line in enumerate(lines):
        if line == "### Observations":
            in_observations = True
            continue
        if line == "### Proposals":
            in_observations = False
            in_proposals = True
            continue
        if line.startswith("### "):
            in_observations = False
            in_proposals = False
        if in_observations:
            security_match = SECURITY_OBSERVATION.fullmatch(line)
            if security_match:
                evidence_text = ""
                for following in lines[index + 1:]:
                    if following.startswith("- ") or following.startswith("### "):
                        break
                    evidence_match = EVIDENCE_LINE.fullmatch(following)
                    if evidence_match:
                        evidence_text = evidence_match.group(1)
                        break
                references = TOKEN.findall(evidence_text)
                evidence = [verify_reference(reference) for reference in references]
                matched = bool(evidence) and all(item["matched"] for item in evidence)
                status = (
                    "CRITICAL-SECURITY-OBJECT-MATCHED" if matched
                    else "UNVERIFIED-SECURITY"
                )
                lines[index] = SECURITY_OBSERVATION.sub(f"- [{status}] \\1", line)
                security_findings.append({
                    "line": index + 1,
                    "finding": security_match.group(1),
                    "status": status,
                    "evidence": evidence,
                    "reason": "" if matched else (
                        "no primary evidence declared" if not references
                        else "one or more primary witnesses failed"
                    ),
                })
                continue
            observation_match = OBSERVATION.fullmatch(line)
            if observation_match:
                evidence_text = ""
                for following in lines[index + 1:]:
                    if following.startswith("- ") or following.startswith("### "):
                        break
                    evidence_match = EVIDENCE_LINE.fullmatch(following)
                    if evidence_match:
                        evidence_text = evidence_match.group(1)
                        break
                references = TOKEN.findall(evidence_text)
                evidence = [verify_reference(reference) for reference in references]
                prescriptive = bool(PRESCRIPTIVE_LANGUAGE.search(observation_match.group(1)))
                matched = (
                    bool(evidence)
                    and all(item["matched"] for item in evidence)
                    and not prescriptive
                )
                status = (
                    "OBSERVATION-OBJECT-MATCHED" if matched
                    else "UNVERIFIED-OBSERVATION"
                )
                lines[index] = OBSERVATION.sub(f"- [{status}] \\1", line)
                observations.append({
                    "line": index + 1,
                    "finding": observation_match.group(1),
                    "status": status,
                    "evidence": evidence,
                    "reason": "" if matched else (
                        "prescriptive language is not an observation"
                        if prescriptive else (
                            "no primary evidence declared" if not references
                            else "one or more primary witnesses failed"
                        )
                    ),
                })
        if not in_proposals:
            continue
        match = PROPOSAL.fullmatch(line)
        if match:
            evidence_text = ""
            for following in lines[index + 1:]:
                if PROPOSAL.fullmatch(following) or following.startswith("### "):
                    break
                evidence_match = EVIDENCE_LINE.fullmatch(following)
                if evidence_match:
                    evidence_text = evidence_match.group(1)
                    break
            references = TOKEN.findall(evidence_text)
            evidence = [verify_reference(reference) for reference in references]
            matched = bool(evidence) and all(item["matched"] for item in evidence)
            lines[index] = PROPOSAL.sub(
                f"- [{'PRIMARY-OBJECT-MATCHED' if matched else 'UNVERIFIED'}] `\\1` — \\2", line
            )
            proposals.append({
                "line": index + 1,
                "target": match.group(1),
                "change": match.group(2),
                "status": "PRIMARY-OBJECT-MATCHED" if matched else "UNVERIFIED",
                "evidence": evidence,
                "reason": "" if matched else (
                    "no primary evidence declared" if not references
                    else "one or more primary witnesses failed"
                ),
            })
        elif re.match(r"^(?:[-*]|[0-9]+\.)\s+", line):
            unstructured.append({"line": index + 1, "text": line})

    if unstructured:
        proposals.extend({
            "line": item["line"],
            "target": "",
            "change": item["text"],
            "status": "UNVERIFIED",
            "evidence": [],
            "reason": "proposal does not use the machine-readable contract",
        } for item in unstructured)

    payload = {
        "schema_version": 3,
        "attestation_scope": (
            "PRIMARY-OBJECT-MATCHED means every declared primary-object reference "
            "resolved and matched exactly; it does not establish that the evidence "
            "entails the proposal or that the proposal should be executed."
        ),
        "reflection": str(artifact_path or reflection),
        "observed_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "proposal_count": len(proposals),
        "primary_object_matched_count": sum(
            item["status"] == "PRIMARY-OBJECT-MATCHED" for item in proposals
        ),
        "unverified_count": sum(item["status"] == "UNVERIFIED" for item in proposals),
        "proposals": proposals,
        "observation_count": len(observations),
        "observation_object_matched_count": sum(
            item["status"] == "OBSERVATION-OBJECT-MATCHED" for item in observations
        ),
        "unverified_observation_count": sum(
            item["status"] == "UNVERIFIED-OBSERVATION" for item in observations
        ),
        "observations": observations,
        "critical_security_count": len(security_findings),
        "critical_security_object_matched_count": sum(
            item["status"] == "CRITICAL-SECURITY-OBJECT-MATCHED"
            for item in security_findings
        ),
        "unverified_security_count": sum(
            item["status"] == "UNVERIFIED-SECURITY" for item in security_findings
        ),
        "security_findings": security_findings,
    }
    reflection_text = ("\n".join(lines) + "\n").encode()
    atomic_write(reflection, reflection_text)
    sidecar_text = (json.dumps(payload, indent=2, sort_keys=True) + "\n").encode()
    atomic_write(sidecar, sidecar_text)
    return payload


def update_invocation_manifest(
    manifest_path: Path,
    reflection: Path,
    artifact_path: Path,
    sidecar: Path,
    artifact_sidecar_path: Path,
    payload: dict[str, object],
) -> None:
    manifest = json.loads(read_regular_file(manifest_path, MAX_REFLECTION_BYTES))
    final_reflection = read_regular_file(reflection, MAX_REFLECTION_BYTES)
    final_sidecar = read_regular_file(sidecar, MAX_REFLECTION_BYTES)
    manifest["pre_attestation_reflection"] = manifest.get("reflection", {})
    manifest["reflection"] = {
        "path": str(artifact_path),
        "bytes": len(final_reflection),
        "sha256": digest_bytes(final_reflection),
    }
    manifest["primary_object_attestation"] = {
        "path": str(artifact_sidecar_path),
        "bytes": len(final_sidecar),
        "sha256": digest_bytes(final_sidecar),
        "proposal_count": payload["proposal_count"],
        "primary_object_matched_count": payload["primary_object_matched_count"],
        "unverified_count": payload["unverified_count"],
        "observation_count": payload["observation_count"],
        "observation_object_matched_count": payload[
            "observation_object_matched_count"
        ],
        "unverified_observation_count": payload["unverified_observation_count"],
        "critical_security_count": payload["critical_security_count"],
        "critical_security_object_matched_count": payload[
            "critical_security_object_matched_count"
        ],
        "unverified_security_count": payload["unverified_security_count"],
    }
    atomic_write(
        manifest_path,
        (json.dumps(manifest, indent=2, sort_keys=True) + "\n").encode(),
    )


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("reflection", type=Path)
    parser.add_argument("--sidecar", required=True, type=Path)
    parser.add_argument("--artifact-path", type=Path)
    parser.add_argument("--artifact-sidecar-path", type=Path)
    parser.add_argument("--finalize-manifest", type=Path)
    args = parser.parse_args()
    if args.finalize_manifest:
        if not args.artifact_path or not args.artifact_sidecar_path:
            parser.error(
                "--finalize-manifest requires --artifact-path and "
                "--artifact-sidecar-path"
            )
        payload = json.loads(read_regular_file(args.sidecar, MAX_REFLECTION_BYTES))
        payload["reflection"] = str(args.artifact_path)
        atomic_write(
            args.sidecar,
            (json.dumps(payload, indent=2, sort_keys=True) + "\n").encode(),
        )
        update_invocation_manifest(
            args.finalize_manifest, args.reflection, args.artifact_path,
            args.sidecar, args.artifact_sidecar_path, payload,
        )
    else:
        payload = witness(args.reflection, args.sidecar)
    print(json.dumps({
        "proposal_count": payload["proposal_count"],
        "primary_object_matched_count": payload["primary_object_matched_count"],
        "unverified_count": payload["unverified_count"],
        "observation_count": payload["observation_count"],
        "observation_object_matched_count": payload[
            "observation_object_matched_count"
        ],
        "unverified_observation_count": payload["unverified_observation_count"],
        "critical_security_count": payload["critical_security_count"],
        "critical_security_object_matched_count": payload[
            "critical_security_object_matched_count"
        ],
        "unverified_security_count": payload["unverified_security_count"],
    }, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
