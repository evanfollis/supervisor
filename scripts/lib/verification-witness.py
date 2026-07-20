#!/usr/bin/env python3
"""Deterministic witness for a repository's declared runnable test surface.

The witness does not execute test bodies. It resolves inventory through the
repository's declared runner semantics, then verifies exact counts and stable
fingerprints. This catches empty/wrong discovery roots before a green runner can
be mistaken for evidence.
"""

from __future__ import annotations

import argparse
import ast
import hashlib
import json
import subprocess
import sys
from pathlib import Path
from typing import Any

SCHEMA_VERSION = 1
DEFAULT_MANIFEST = ".verification/test-collection.json"
DEFAULT_EXCLUDES = {".git", ".venv", "node_modules", ".next", "dist", "build"}


class WitnessError(ValueError):
    pass


def _fingerprint(values: list[str]) -> str:
    body = "".join(f"{value}\n" for value in sorted(values)).encode("utf-8")
    return hashlib.sha256(body).hexdigest()


def _relative_path(value: object, label: str) -> Path:
    if not isinstance(value, str) or not value.strip():
        raise WitnessError(f"{label} must be a non-empty relative path")
    path = Path(value)
    if path.is_absolute() or ".." in path.parts:
        raise WitnessError(f"{label} must stay inside the repository: {value}")
    return path


def _string_list(value: object, label: str) -> list[str]:
    if not isinstance(value, list) or not value:
        raise WitnessError(f"{label} must be a non-empty list")
    if any(not isinstance(item, str) or not item for item in value):
        raise WitnessError(f"{label} entries must be non-empty strings")
    return value


def _load_manifest(path: Path) -> dict[str, Any]:
    if path.is_symlink() or not path.is_file():
        raise WitnessError(f"manifest must be a regular non-symlink file: {path}")
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise WitnessError(f"manifest not found: {path}") from exc
    except json.JSONDecodeError as exc:
        raise WitnessError(f"manifest is not valid JSON: {exc}") from exc
    if not isinstance(payload, dict) or payload.get("schema_version") != SCHEMA_VERSION:
        raise WitnessError(f"manifest schema_version must be {SCHEMA_VERSION}")
    if not isinstance(payload.get("collectors"), list) or not payload["collectors"]:
        raise WitnessError("manifest.collectors must be a non-empty list")
    return payload


def _tracked_files(repo: Path) -> set[str]:
    result = subprocess.run(
        ["git", "-C", str(repo), "ls-files", "-z"],
        capture_output=True,
        timeout=20,
    )
    if result.returncode != 0:
        raise WitnessError(f"repository is not readable by git: {repo}")
    return {
        raw.decode("utf-8")
        for raw in result.stdout.split(b"\0")
        if raw
    }


def _collect_files(repo: Path, collector: dict[str, Any], label: str) -> list[Path]:
    roots = _string_list(collector.get("roots"), f"{label}.roots")
    includes = _string_list(collector.get("include"), f"{label}.include")
    exclude_dirs = set(collector.get("exclude_dirs") or []) | DEFAULT_EXCLUDES
    if any(not isinstance(item, str) or not item for item in exclude_dirs):
        raise WitnessError(f"{label}.exclude_dirs entries must be non-empty strings")

    collected: set[Path] = set()
    repo_resolved = repo.resolve()
    for root_value in roots:
        root_rel = _relative_path(root_value, f"{label}.roots")
        root = repo / root_rel
        if not root.is_dir() or root.is_symlink():
            raise WitnessError(f"{label} root must be a real directory: {root_rel}")
        if not root.resolve().is_relative_to(repo_resolved):
            raise WitnessError(f"{label} root escapes repository: {root_rel}")
        for pattern in includes:
            for path in root.rglob(pattern):
                relative = path.relative_to(repo)
                if any(part in exclude_dirs for part in relative.parts):
                    continue
                if path.is_symlink() or not path.is_file():
                    continue
                collected.add(relative)
    if len(collected) > 10_000:
        raise WitnessError(f"{label} collected more than 10,000 files")
    return sorted(collected, key=lambda path: path.as_posix())


def _python_explicit_ids(repo: Path, files: list[Path], label: str) -> list[str]:
    """Read an explicit TESTS list without importing or executing repo code."""
    ids: list[str] = []
    for relative in files:
        try:
            module = ast.parse((repo / relative).read_text(encoding="utf-8"))
        except (OSError, UnicodeDecodeError, SyntaxError) as exc:
            raise WitnessError(f"{label} cannot parse {relative}: {exc}") from exc
        functions = {
            node.name
            for node in module.body
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))
        }
        assignments = [
            node for node in module.body
            if isinstance(node, ast.Assign)
            and any(isinstance(target, ast.Name) and target.id == "TESTS"
                    for target in node.targets)
        ]
        if len(assignments) != 1 or not isinstance(assignments[0].value, (ast.List, ast.Tuple)):
            raise WitnessError(
                f"{label} requires one literal TESTS list in {relative}; "
                "computed discovery is not auditable"
            )
        elements = assignments[0].value.elts
        if not elements or any(not isinstance(element, ast.Name) for element in elements):
            raise WitnessError(
                f"{label} TESTS in {relative} must be a non-empty list of function names"
            )
        names = [element.id for element in elements]
        if len(names) != len(set(names)):
            raise WitnessError(f"{label} TESTS in {relative} contains duplicate names")
        missing = [name for name in names if name not in functions]
        if missing:
            raise WitnessError(
                f"{label} TESTS in {relative} names undefined functions: "
                + ", ".join(missing)
            )
        test_functions = {name for name in functions if name.startswith("test_")}
        unlisted = sorted(test_functions - set(names))
        if unlisted:
            raise WitnessError(
                f"{label} found test functions missing from TESTS in {relative}: "
                + ", ".join(unlisted)
            )
        ids.extend(f"{relative.as_posix()}::{name}" for name in names)
    return sorted(ids)


def observe(repo: Path, manifest_path: Path) -> dict[str, Any]:
    manifest = _load_manifest(manifest_path)
    tracked = _tracked_files(repo)
    try:
        manifest_relative = manifest_path.resolve().relative_to(repo.resolve()).as_posix()
    except ValueError as exc:
        raise WitnessError("manifest must live inside the repository") from exc
    if manifest_relative not in tracked:
        raise WitnessError(f"manifest is not git-tracked: {manifest_relative}")

    seen_ids: set[str] = set()
    results = []
    for index, raw in enumerate(manifest["collectors"]):
        label = f"collectors[{index}]"
        if not isinstance(raw, dict):
            raise WitnessError(f"{label} must be an object")
        collector_id = raw.get("id")
        if not isinstance(collector_id, str) or not collector_id:
            raise WitnessError(f"{label}.id must be a non-empty string")
        if collector_id in seen_ids:
            raise WitnessError(f"duplicate collector id: {collector_id}")
        seen_ids.add(collector_id)
        mode = raw.get("mode")
        if mode not in {"files", "python-explicit-tests"}:
            raise WitnessError(
                f"{label}.mode must be files or python-explicit-tests"
            )
        files = _collect_files(repo, raw, label)
        file_names = [path.as_posix() for path in files]
        if not file_names:
            raise WitnessError(
                f"{collector_id} collected zero files; an empty test surface is never evidence"
            )
        untracked = [path for path in file_names if path not in tracked]
        if untracked:
            raise WitnessError(
                f"{collector_id} collected untracked test files: {', '.join(untracked[:5])}"
            )
        result: dict[str, Any] = {
            "id": collector_id,
            "mode": mode,
            "file_count": len(file_names),
            "file_fingerprint": _fingerprint(file_names),
            "files": file_names,
        }
        if mode == "python-explicit-tests":
            case_ids = _python_explicit_ids(repo, files, collector_id)
            result.update({
                "case_count": len(case_ids),
                "case_fingerprint": _fingerprint(case_ids),
                "cases": case_ids,
            })
        results.append(result)
    return {"schema_version": SCHEMA_VERSION, "collectors": results}


def verify(repo: Path, manifest_path: Path) -> dict[str, Any]:
    manifest = _load_manifest(manifest_path)
    observed = observe(repo, manifest_path)
    problems = []
    for declared, actual in zip(manifest["collectors"], observed["collectors"]):
        label = actual["id"]
        fields = ["files"]
        if actual["mode"] == "python-explicit-tests":
            fields.append("cases")
        for field in fields:
            expected = _string_list(declared.get(field), f"{label}.{field}")
            if expected != actual[field]:
                expected_set, actual_set = set(expected), set(actual[field])
                added = sorted(actual_set - expected_set)
                removed = sorted(expected_set - actual_set)
                if added:
                    problems.append(f"{label} {field} added: {', '.join(added)}")
                if removed:
                    problems.append(f"{label} {field} removed: {', '.join(removed)}")
                if not added and not removed:
                    problems.append(f"{label} {field} order changed")
    if problems:
        detail = "\n  - ".join(problems)
        raise WitnessError(
            "test collection differs from the declared witness:\n  - " + detail
            + "\nRun with --observe to inspect the intended new inventory. "
              "The manifest stores identities directly so additions/removals remain reviewable."
        )
    return observed


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("repo", nargs="?", default=".")
    parser.add_argument("--manifest", default=DEFAULT_MANIFEST)
    parser.add_argument("--observe", action="store_true")
    args = parser.parse_args()
    repo = Path(args.repo).resolve()
    manifest_path = Path(args.manifest)
    if not manifest_path.is_absolute():
        manifest_path = repo / manifest_path
    try:
        result = (
            observe(repo, manifest_path)
            if args.observe
            else verify(repo, manifest_path)
        )
    except (WitnessError, OSError, subprocess.SubprocessError) as exc:
        print(f"test-collection witness FAIL: {exc}", file=sys.stderr)
        return 1
    if args.observe:
        print(json.dumps(result, indent=2, sort_keys=True))
    else:
        total_files = sum(item.get("file_count", 0) for item in result["collectors"])
        total_cases = sum(item.get("case_count", 0) for item in result["collectors"])
        print(
            f"test-surface witness PASS — {len(result['collectors'])} collector(s), "
            f"{total_files} file(s), {total_cases} runner-declared case(s)"
        )
    return 0


if __name__ == "__main__":
    sys.exit(main())
