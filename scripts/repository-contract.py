#!/usr/bin/env python3
"""Validate the thin ADR-0050 declaration and front-door contract.

This checker validates metadata shape, required front-door presence, declared
artifact hygiene, workspace-risk ceilings, and central-inventory divergence. A
green result is not full ADR-0050 conformance: shape semantics, instruction
quality/size, artifact-list completeness, containment, deployment, and real
outcomes require their own profile-specific gates and receipts.
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
import tomllib
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

SHAPES = {
    "service",
    "application",
    "library",
    "monorepo",
    "contract",
    "context",
    "control-plane",
    "profile",
}
LIFECYCLES = {"active", "maintained", "case-study", "archived"}
RISKS = {"none", "model-assisted", "agentic"}
RISK_RANK = {"none": 0, "model-assisted": 1, "agentic": 2}
ARTIFACT_ROLES = {"authoritative", "runtime", "generated", "historical"}
REQUIRED_ROOT = ("README.md", "repo.toml", "Makefile", "AGENTS.md", "CLAUDE.md")


@dataclass(frozen=True)
class Finding:
    repository: str
    code: str
    message: str


def load_toml(path: Path) -> dict[str, Any]:
    with path.open("rb") as handle:
        return tomllib.load(handle)


def ignored_by_git(root: Path, relative: str) -> bool:
    result = subprocess.run(
        ["git", "-C", str(root), "check-ignore", "--quiet", "--", relative],
        check=False,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    return result.returncode == 0


def validate_repo(
    root: Path, *, expected_name: str | None = None, expected_remote: str | None = None
) -> list[Finding]:
    findings: list[Finding] = []
    label = expected_name or root.name
    declaration_path = root / "repo.toml"
    if not root.is_dir():
        return [Finding(label, "repository-missing", f"path does not exist: {root}")]
    if not declaration_path.is_file():
        return [Finding(label, "declaration-missing", "repo.toml is missing")]

    try:
        declaration = load_toml(declaration_path)
    except (OSError, tomllib.TOMLDecodeError) as error:
        return [Finding(label, "declaration-invalid", str(error))]

    schema_version = declaration.get("schema_version")
    if type(schema_version) is not int or schema_version != 1:
        findings.append(
            Finding(label, "schema-version", f"expected 1, found {schema_version!r}")
        )

    name = declaration.get("name")
    if not isinstance(name, str) or not name:
        findings.append(Finding(label, "name-invalid", "name must be a non-empty string"))
    elif expected_name and name != expected_name:
        findings.append(
            Finding(label, "name-divergence", f"repo.toml={name!r}, inventory={expected_name!r}")
        )

    for key, allowed in (
        ("shape", SHAPES),
        ("lifecycle", LIFECYCLES),
        ("agentic_risk", RISKS),
    ):
        value = declaration.get(key)
        if value not in allowed:
            findings.append(
                Finding(label, f"{key}-invalid", f"{key} must be one of {sorted(allowed)}")
            )

    remote = declaration.get("canonical_repository")
    if not isinstance(remote, str) or not remote.startswith("https://github.com/"):
        findings.append(
            Finding(
                label,
                "canonical-repository-invalid",
                "canonical_repository must be a GitHub HTTPS repository URL",
            )
        )
    elif expected_remote and remote.rstrip("/") != expected_remote.rstrip("/"):
        findings.append(
            Finding(
                label,
                "canonical-repository-divergence",
                f"repo.toml={remote!r}, inventory={expected_remote!r}",
            )
        )

    if declaration.get("shape") != "profile":
        for relative in REQUIRED_ROOT:
            if not (root / relative).exists():
                findings.append(
                    Finding(label, "front-door-missing", f"required path missing: {relative}")
                )
        if not any(
            (root / candidate).is_file()
            for candidate in ("docs/architecture.md", "docs/ARCHITECTURE.md")
        ):
            findings.append(
                Finding(
                    label,
                    "architecture-missing",
                    "docs/architecture.md is missing",
                )
            )

    artifacts = declaration.get("artifacts")
    if artifacts is not None:
        if not isinstance(artifacts, dict):
            findings.append(Finding(label, "artifacts-invalid", "artifacts must be a table"))
        else:
            unknown = set(artifacts) - ARTIFACT_ROLES
            for role in sorted(unknown):
                findings.append(
                    Finding(label, "artifact-role-invalid", f"unknown artifact role: {role}")
                )
            for role in sorted(ARTIFACT_ROLES & set(artifacts)):
                entries = artifacts[role]
                if not isinstance(entries, list) or not all(
                    isinstance(item, str) and item for item in entries
                ):
                    findings.append(
                        Finding(
                            label,
                            "artifact-path-invalid",
                            f"artifacts.{role} must be a list of non-empty paths",
                        )
                    )
                    continue
                for relative in entries:
                    if Path(relative).is_absolute() or ".." in Path(relative).parts:
                        findings.append(
                            Finding(
                                label,
                                "artifact-path-unsafe",
                                f"artifacts.{role} is not repo-relative: {relative}",
                            )
                        )
                        continue
                    path_exists = (root / relative).exists()
                    if role not in {"runtime", "generated"} and not path_exists:
                        findings.append(
                            Finding(
                                label,
                                "artifact-path-missing",
                                f"artifacts.{role} path does not exist: {relative}",
                            )
                        )
                    if role in {"runtime", "generated"} and not ignored_by_git(root, relative):
                        findings.append(
                            Finding(
                                label,
                                "artifact-path-tracked-risk",
                                f"artifacts.{role} path is not gitignored: {relative}",
                            )
                        )

    root_risk = declaration.get("agentic_risk")
    workspaces = declaration.get("workspaces", {})
    if workspaces is not None and not isinstance(workspaces, dict):
        findings.append(Finding(label, "workspaces-invalid", "workspaces must be a table"))
    elif isinstance(workspaces, dict):
        for workspace, values in sorted(workspaces.items()):
            risk = values.get("agentic_risk") if isinstance(values, dict) else None
            if risk not in RISKS:
                findings.append(
                    Finding(
                        label,
                        "workspace-risk-invalid",
                        f"workspaces.{workspace}.agentic_risk must be one of {sorted(RISKS)}",
                    )
                )
            elif root_risk in RISKS and RISK_RANK[risk] > RISK_RANK[root_risk]:
                findings.append(
                    Finding(
                        label,
                        "workspace-risk-exceeds-root",
                        f"workspaces.{workspace}={risk!r} exceeds root={root_risk!r}",
                    )
                )

    return findings


def load_session_inventory(path: Path) -> dict[str, Path]:
    sessions: dict[str, Path] = {}
    for raw_line in path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#"):
            continue
        parts = line.split("|")
        if len(parts) < 2 or not parts[0] or not parts[1]:
            raise ValueError(f"invalid session inventory line: {raw_line!r}")
        sessions[parts[0]] = Path(parts[1]).resolve()
    return sessions


def validate_inventory(path: Path, allow_missing: bool = False) -> tuple[list[Finding], int]:
    # `allow_missing` is retained as a CLI compatibility argument. Per-repo
    # `conformance` is the only authority for migration allowances.
    del allow_missing
    inventory = load_toml(path)
    if inventory.get("schema_version") != 1:
        return [Finding("inventory", "schema-version", "expected schema_version = 1")], 0
    repositories = inventory.get("repositories")
    if not isinstance(repositories, list):
        return [Finding("inventory", "repositories-invalid", "repositories must be an array")], 0

    findings: list[Finding] = []
    sessions: dict[str, Path] | None = None
    session_inventory = inventory.get("session_inventory")
    if session_inventory is not None:
        if not isinstance(session_inventory, str) or not session_inventory:
            findings.append(
                Finding(
                    "inventory",
                    "session-inventory-invalid",
                    "session_inventory must be a non-empty path",
                )
            )
        else:
            session_path = (path.parent / session_inventory).resolve()
            try:
                sessions = load_session_inventory(session_path)
            except (OSError, ValueError) as error:
                findings.append(
                    Finding("inventory", "session-inventory-invalid", str(error))
                )

    checked = 0
    for entry in repositories:
        if not isinstance(entry, dict):
            findings.append(
                Finding("inventory", "repository-entry-invalid", "entry must be a table")
            )
            continue
        name = entry.get("name")
        root_value = entry.get("path")
        remote = entry.get("canonical_repository")
        if not isinstance(name, str) or not isinstance(root_value, str):
            findings.append(
                Finding("inventory", "repository-entry-invalid", "name and path are required")
            )
            continue
        root = Path(root_value)
        if not root.is_absolute():
            findings.append(
                Finding(name, "repository-path-invalid", "inventory path must be absolute")
            )
        conformance = entry.get("conformance")
        if conformance not in {"migrating", "conforming"}:
            findings.append(
                Finding(
                    name,
                    "conformance-invalid",
                    "conformance must be 'migrating' or 'conforming'",
                )
            )
        session = entry.get("session")
        if not isinstance(session, str) or not session:
            findings.append(
                Finding(name, "session-invalid", "session must be a non-empty string")
            )
        elif sessions is not None:
            session_root = sessions.get(session)
            if session_root is None:
                findings.append(
                    Finding(name, "session-unknown", f"session is not registered: {session}")
                )
            else:
                try:
                    root.resolve().relative_to(session_root)
                except ValueError:
                    findings.append(
                        Finding(
                            name,
                            "session-path-divergence",
                            f"repository path {root} is outside session root {session_root}",
                        )
                    )
        repo_findings = validate_repo(root, expected_name=name, expected_remote=remote)
        if conformance == "migrating":
            repo_findings = [
                finding
                for finding in repo_findings
                if finding.code not in {"declaration-missing", "front-door-missing", "architecture-missing"}
            ]
        findings.extend(repo_findings)
        checked += 1
    return findings, checked


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("repositories", nargs="*", type=Path)
    parser.add_argument("--inventory", type=Path)
    parser.add_argument(
        "--allow-missing",
        action="store_true",
        help="deprecated compatibility flag; per-repository conformance controls allowances",
    )
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    if bool(args.inventory) == bool(args.repositories):
        parser.error("provide either repository paths or --inventory")

    if args.inventory:
        findings, checked = validate_inventory(args.inventory, args.allow_missing)
    else:
        checked = len(args.repositories)
        findings = []
        for root in args.repositories:
            findings.extend(validate_repo(root.resolve()))

    if args.json:
        print(
            json.dumps(
                {"checked": checked, "ok": not findings, "findings": [asdict(f) for f in findings]},
                indent=2,
                sort_keys=True,
            )
        )
    else:
        for finding in findings:
            print(f"{finding.repository}: {finding.code}: {finding.message}", file=sys.stderr)
        print(f"repository-contract: checked={checked} findings={len(findings)}")
    return 1 if findings else 0


if __name__ == "__main__":
    raise SystemExit(main())
