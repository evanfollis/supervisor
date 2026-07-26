#!/usr/bin/env python3
"""Validate ADR-0050 repository declarations and front doors."""

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
    if schema_version != 1:
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
                    if not (root / relative).exists():
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

    return findings


def validate_inventory(path: Path, allow_missing: bool) -> tuple[list[Finding], int]:
    inventory = load_toml(path)
    if inventory.get("schema_version") != 1:
        return [Finding("inventory", "schema-version", "expected schema_version = 1")], 0
    repositories = inventory.get("repositories")
    if not isinstance(repositories, list):
        return [Finding("inventory", "repositories-invalid", "repositories must be an array")], 0

    findings: list[Finding] = []
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
        repo_findings = validate_repo(root, expected_name=name, expected_remote=remote)
        if allow_missing:
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
    parser.add_argument("--allow-missing", action="store_true")
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
