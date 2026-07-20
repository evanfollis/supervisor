#!/usr/bin/env python3
"""Contract tests for the reflection document envelope."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from reflection_document import normalize, normalize_with_metadata  # noqa: E402


VALID = """### Summary
Summary.
### Principle adherence
Measured.
### Observations
Observed.
### Proposals
No proposals in this window.
### Questions for the human

None.
"""


def test_preamble_is_removed_without_losing_the_raw_transcript():
    value, metadata = normalize_with_metadata("I inspected the artifacts.\n\n---\n" + VALID)
    assert value == VALID
    assert metadata["preamble_lines_removed"] == 3


def test_questions_are_suppressed_from_projection_but_counted():
    value, metadata = normalize_with_metadata(
        VALID.replace("None.\n", "1. Where is the implementation?\n2. Who made the commit?\n")
    )
    assert value.endswith("### Questions for the human\n\nNone.\n")
    assert metadata["question_lines_suppressed"] == 2


def test_missing_or_duplicate_sections_fail_closed():
    try:
        normalize(VALID.replace("### Observations\n", ""))
    except ValueError as error:
        assert "Observations" in str(error)
    else:
        raise AssertionError("missing section was accepted")
    try:
        normalize(VALID + "### Summary\nAgain\n")
    except ValueError as error:
        assert "exactly one" in str(error)
    else:
        raise AssertionError("duplicate section was accepted")


def test_section_order_is_enforced():
    wrong = VALID.replace(
        "### Principle adherence\nMeasured.\n### Observations\nObserved.",
        "### Observations\nObserved.\n### Principle adherence\nMeasured.",
    )
    try:
        normalize(wrong)
    except ValueError as error:
        assert "out of order" in str(error)
    else:
        raise AssertionError("out-of-order document was accepted")


TESTS = [
    test_missing_or_duplicate_sections_fail_closed,
    test_preamble_is_removed_without_losing_the_raw_transcript,
    test_questions_are_suppressed_from_projection_but_counted,
    test_section_order_is_enforced,
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
