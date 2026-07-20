#!/usr/bin/env python3
"""Normalize and validate the stable reflection document envelope."""

from __future__ import annotations

REQUIRED_HEADINGS = [
    "### Summary",
    "### Principle adherence",
    "### Observations",
    "### Proposals",
    "### Questions for the human",
]
MAX_LINES = 400


def normalize_with_metadata(value: str) -> tuple[str, dict[str, int]]:
    lines = value.splitlines()
    try:
        start = lines.index(REQUIRED_HEADINGS[0])
    except ValueError as error:
        raise ValueError("reflection has no exact '### Summary' heading") from error
    preamble_lines_removed = start
    lines = lines[start:]
    if len(lines) > MAX_LINES:
        raise ValueError(f"reflection exceeds {MAX_LINES} lines")
    positions: list[int] = []
    for heading in REQUIRED_HEADINGS:
        matches = [index for index, line in enumerate(lines) if line == heading]
        if len(matches) != 1:
            raise ValueError(f"reflection requires exactly one {heading!r} heading")
        positions.append(matches[0])
    if positions != sorted(positions) or len(set(positions)) != len(positions):
        raise ValueError("reflection headings are out of order")
    questions_index = positions[-1]
    suppressed = [line for line in lines[questions_index + 1:] if line.strip()]
    lines = lines[:questions_index + 1] + ["", "None."]
    return "\n".join(lines).rstrip() + "\n", {
        "preamble_lines_removed": preamble_lines_removed,
        "question_lines_suppressed": len(suppressed),
    }


def normalize(value: str) -> str:
    return normalize_with_metadata(value)[0]
