#!/usr/bin/env python3
"""Validate the narrow ADR-0047 provenance contract for project handoffs."""

from __future__ import annotations

import os
import sys
from datetime import datetime
from pathlib import Path


EMPTY_VALUES = {"", "''", '""', "null", "~", "tbd", "todo"}
REQUIRED = ("authority", "external_dependencies", "policy_compatibility")

# Sentinel: key is present but its value is a YAML block scalar (|,>) or a list.
# The ADR-0047 contract requires single-line scalars; a non-scalar value must be
# reported as such, not silently dropped (which produced a misleading "missing").
NON_SCALAR = "\x00non-scalar"


def fail(message: str) -> None:
    print(message)
    raise SystemExit(1)


def scalar_frontmatter(path: Path) -> dict[str, str]:
    lines = path.read_text(encoding="utf-8").splitlines()
    if not lines or lines[0] != "---":
        fail("missing or unclosed YAML frontmatter")
    try:
        end = lines.index("---", 1)
    except ValueError:
        fail("missing or unclosed YAML frontmatter")

    values: dict[str, str] = {}
    last_key: str | None = None
    for line in lines[1:end]:
        if not line.strip():
            last_key = None
            continue
        if line[:1].isspace():
            # Indented continuation: a block-scalar body or a "- item" list
            # element. Its parent key is therefore non-scalar. Record that
            # instead of dropping it (the old behavior misreported it as missing).
            if last_key is not None:
                values[last_key] = NON_SCALAR
            continue
        if ":" not in line:
            last_key = None
            continue
        key, value = line.split(":", 1)
        key, value = key.strip(), value.strip()
        if value[:1] in ("|", ">"):  # YAML block-scalar indicator
            value = NON_SCALAR
        values[key] = value
        last_key = key
    return values


def meaningful(value: str | None) -> bool:
    if value is None:
        return False
    normalized = value.strip().lower()
    return normalized not in EMPTY_VALUES and not normalized.startswith("#")


def main() -> None:
    if len(sys.argv) not in (2, 3):
        fail("usage: check-handoff-provenance.py FILE [CUTOFF_ISO]")
    path = Path(sys.argv[1])
    cutoff = datetime.fromisoformat(
        (sys.argv[2] if len(sys.argv) == 3 else "2026-07-12T12:56:00Z").replace("Z", "+00:00")
    ).timestamp()

    # ctime cannot be preserved or backdated with normal copy/touch operations.
    # mtime would let a new handoff bypass the cutover via cp -p or touch -d.
    if os.stat(path).st_ctime < cutoff:
        return

    values = scalar_frontmatter(path)
    nonscalar = [key for key in REQUIRED if values.get(key) == NON_SCALAR]
    if nonscalar:
        fail("non-scalar provenance fields (must be single-line scalars): "
             + " ".join(nonscalar))
    missing = [key for key in REQUIRED if not meaningful(values.get(key))]
    if missing:
        fail(f"missing required provenance fields: {' '.join(missing)}")

    dependency_class = values["external_dependencies"].lower()
    if dependency_class not in {"none", "authorized"}:
        fail("external_dependencies must be the scalar enum 'none' or 'authorized'")
    if dependency_class == "authorized":
        extra_missing = [
            key for key in ("dependency_authority", "dependency_details")
            if not meaningful(values.get(key))
        ]
        if extra_missing:
            fail(
                "authorized external dependency missing fields: "
                + " ".join(extra_missing)
            )


if __name__ == "__main__":
    try:
        main()
    except (OSError, UnicodeError, ValueError) as exc:
        print(f"provenance checker internal error: {type(exc).__name__}: {exc}")
        raise SystemExit(2) from exc
