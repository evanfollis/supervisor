#!/usr/bin/env python3
"""Regression tests for the prompteval subscription-CLI harness fallback logic.

Covers the failure class where a hung/empty provider was falsely scored as
success and never fell back to the sibling subscription CLI:

  - timeout           -> ProviderUnavailable -> fall back once to sibling
  - exit 0 + empty    -> ProviderUnavailable -> fall back once to sibling
  - semantic error    -> LLMCallError, FAIL-CLOSED (no fallback)
  - all unavailable   -> AllProvidersThrottled (hard stop)
  - executor exit 0 + empty -> RunError (truthful), not a false empty success

Runnable standalone (`python3 test_harness_fallback.py`) or under pytest.
"""

import os
import subprocess
import sys
import tempfile
from pathlib import Path
from unittest import mock

# Isolate the circuit breaker from these fallback-focused tests: a throwaway
# state file and an unreachable threshold keep it transparent (always "attempt",
# never opens), so real runtime state is untouched and no state bleeds between
# tests. Must be set before importing the package (constants read at import).
os.environ["PROMPTEVAL_CIRCUIT_FILE"] = os.path.join(
    tempfile.gettempdir(), f"pe-circuit-fallback-test-{os.getpid()}.json")
os.environ["PROMPTEVAL_CIRCUIT_THRESHOLD"] = "999999"
# Decisive reasons (timeout/empty) open on first failure regardless of threshold,
# so also empty the decisive set to keep the breaker fully transparent here.
os.environ["PROMPTEVAL_CIRCUIT_DECISIVE_REASONS"] = ""

# Make `prompteval` importable when run directly.
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from prompteval import llm, runner  # noqa: E402


def _proc(returncode=0, stdout="", stderr=""):
    return subprocess.CompletedProcess(args=["x"], returncode=returncode,
                                       stdout=stdout, stderr=stderr)


def _calls():
    return [
        llm.CliCall("claude", "sonnet", ["claude", "-p"]),
        llm.CliCall("codex", "gpt-5", ["codex", "exec"], fallback_from="claude"),
    ]


def _run_fallback(side_effect, emitted):
    with mock.patch.object(llm.subprocess, "run", side_effect=side_effect) as m, \
         mock.patch.object(llm, "emit_llm_call",
                           side_effect=lambda **kw: emitted.append(kw)), \
         mock.patch.object(llm.time, "sleep"):
        result = llm.run_with_fallback(_calls(), timeout=5, retries=0)
    return result, m


def test_timeout_falls_back_to_sibling():
    emitted = []
    result, m = _run_fallback(
        [subprocess.TimeoutExpired(cmd="claude", timeout=5), _proc(0, "sibling answer")],
        emitted)
    assert result == "sibling answer", result
    assert m.call_count == 2, "sibling provider must be tried after a timeout"
    print("ok: timeout -> fallback to sibling")


def test_empty_output_falls_back_and_is_not_success():
    emitted = []
    result, m = _run_fallback([_proc(0, "   \n"), _proc(0, "real answer")], emitted)
    assert result == "real answer", result
    assert m.call_count == 2, "empty exit-0 output must trigger fallback"
    statuses = [e["status"] for e in emitted]
    assert "empty" in statuses, f"empty output must emit truthful status: {statuses}"
    assert "success" not in statuses[:1], "first (empty) call must not read as success"
    print("ok: empty output -> fallback + truthful 'empty' telemetry")


def test_semantic_error_is_fail_closed():
    emitted = []
    with mock.patch.object(llm.subprocess, "run",
                           side_effect=[_proc(1, "", "prompt schema invalid")]) as m, \
         mock.patch.object(llm, "emit_llm_call",
                           side_effect=lambda **kw: emitted.append(kw)), \
         mock.patch.object(llm.time, "sleep"):
        try:
            llm.run_with_fallback(_calls(), timeout=5, retries=0)
            raise AssertionError("semantic error must not be swallowed")
        except llm.LLMCallError:
            pass
    assert m.call_count == 1, "semantic error must NOT fall back to the sibling"
    print("ok: semantic error -> fail-closed, no fallback")


def test_all_providers_unavailable_hard_stops():
    emitted = []
    with mock.patch.object(llm.subprocess, "run",
                           side_effect=[_proc(0, ""), _proc(0, "")]), \
         mock.patch.object(llm, "emit_llm_call",
                           side_effect=lambda **kw: emitted.append(kw)), \
         mock.patch.object(llm.time, "sleep"):
        try:
            llm.run_with_fallback(_calls(), timeout=5, retries=0)
            raise AssertionError("both-empty must raise AllProvidersThrottled")
        except llm.AllProvidersThrottled:
            pass
    print("ok: all providers unavailable -> hard stop")


def test_throttle_still_falls_back():
    emitted = []
    result, m = _run_fallback([_proc(1, "", "429 usage limit reached"),
                               _proc(0, "sibling")], emitted)
    assert result == "sibling", result
    assert m.call_count == 2
    print("ok: throttle -> fallback (regression guard)")


def test_executor_empty_output_is_truthful_error():
    with mock.patch.object(runner.subprocess, "run",
                           side_effect=[_proc(0, "  \n")]):
        try:
            runner._run_cli(["claude", "-p"], stdin_text="x", timeout=5, retries=0)
            raise AssertionError("executor empty output must not be a success")
        except runner.RunError as exc:
            assert "empty output" in str(exc), str(exc)
    print("ok: executor exit-0 empty -> RunError, not false success")


def test_executor_nonempty_output_returns():
    with mock.patch.object(runner.subprocess, "run",
                           side_effect=[_proc(0, "hello")]):
        assert runner._run_cli(["claude", "-p"], stdin_text="x", timeout=5, retries=0) == "hello"
    print("ok: executor exit-0 non-empty -> returns output (regression guard)")


TESTS = [v for k, v in sorted(globals().items()) if k.startswith("test_")]


def main():
    failures = 0
    for t in TESTS:
        try:
            t()
        except AssertionError as exc:
            failures += 1
            print(f"FAIL: {t.__name__}: {exc}")
    print(f"\n{len(TESTS) - failures}/{len(TESTS)} passed")
    sys.exit(1 if failures else 0)


if __name__ == "__main__":
    main()
