#!/usr/bin/env python3
"""Regression tests for the prompteval subscription-CLI harness fallback logic.

Covers bounded same-provider availability retries and optional sibling fallback:

  - one/two timeout or empty failures -> retry the exact provider/model
  - retry exhaustion  -> hard stop when sibling fallback is disabled
  - semantic error    -> LLMCallError, FAIL-CLOSED (no fallback)
  - failed-attempt stdout is never accepted as an answer
  - all unavailable   -> AllProvidersThrottled (hard stop)
  - executor exit 0 + empty -> RunError (truthful), not a false empty success

Runnable standalone (`python3 test_harness_fallback.py`) or under pytest.
"""

import json
import os
import subprocess
import sys
import tempfile
from types import SimpleNamespace
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

from prompteval import grading, llm, runner  # noqa: E402


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
        result = llm.run_with_fallback(_calls(), timeout=5, max_attempts=1)
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
            llm.run_with_fallback(_calls(), timeout=5, max_attempts=3)
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
            llm.run_with_fallback(_calls(), timeout=5, max_attempts=1)
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


def test_expired_auth_falls_back_and_is_not_semantic():
    emitted = []
    result, calls = _run_fallback(
        [
            _proc(
                1,
                "",
                "Failed to authenticate: OAuth session expired and could not be refreshed",
            ),
            _proc(0, "sibling"),
        ],
        emitted,
    )
    assert result == "sibling", result
    assert calls.call_count == 2
    assert [event["status"] for event in emitted] == ["unavailable", "success"]
    print("ok: expired auth -> sibling fallback + truthful unavailable telemetry")


def test_executor_empty_output_is_truthful_error():
    with mock.patch.object(runner.subprocess, "run",
                           side_effect=[_proc(0, "  \n")]):
        try:
            runner._run_cli(
                ["claude", "-p"], stdin_text="x", timeout=5, max_attempts=1
            )
            raise AssertionError("executor empty output must not be a success")
        except runner.RunError as exc:
            assert "empty output" in str(exc), str(exc)
    print("ok: executor exit-0 empty -> RunError, not false success")


def test_executor_nonempty_output_returns():
    with mock.patch.object(runner.subprocess, "run",
                           side_effect=[_proc(0, "hello")]):
        assert runner._run_cli(
            ["claude", "-p"], stdin_text="x", timeout=5, max_attempts=1
        ) == "hello"
    print("ok: executor exit-0 non-empty -> returns output (regression guard)")


def test_one_transient_timeout_recovers_on_same_provider():
    emitted = []
    with mock.patch.object(
        llm.subprocess,
        "run",
        side_effect=[
            subprocess.TimeoutExpired(cmd="claude", timeout=5),
            _proc(0, "recovered answer"),
        ],
    ) as calls, mock.patch.object(
        llm, "emit_llm_call", side_effect=lambda **kw: emitted.append(kw)
    ), mock.patch.object(llm.time, "sleep"):
        result = llm.run_with_fallback(
            _calls(),
            timeout=5,
            max_attempts=3,
            allow_fallback=False,
        )
    assert result == "recovered answer"
    assert calls.call_count == 2
    assert [event["provider"] for event in emitted] == ["claude", "claude"]
    assert [event["status"] for event in emitted] == ["unavailable", "success"]
    print("ok: one transient timeout -> same-provider recovery")


def test_two_transient_empty_results_recover_on_same_provider():
    emitted = []
    with mock.patch.object(
        llm.subprocess,
        "run",
        side_effect=[_proc(0, ""), _proc(0, "  \n"), _proc(0, "third answer")],
    ) as calls, mock.patch.object(
        llm, "emit_llm_call", side_effect=lambda **kw: emitted.append(kw)
    ), mock.patch.object(llm.time, "sleep"):
        result = llm.run_with_fallback(
            _calls(),
            timeout=5,
            max_attempts=3,
            allow_fallback=False,
        )
    assert result == "third answer"
    assert calls.call_count == 3
    assert [event["provider"] for event in emitted] == ["claude"] * 3
    assert [event["status"] for event in emitted] == ["empty", "empty", "success"]
    print("ok: two transient empty results -> same-provider recovery")


def test_same_provider_exhaustion_fails_closed_without_fallback():
    emitted = []
    with mock.patch.object(
        llm.subprocess,
        "run",
        side_effect=[
            subprocess.TimeoutExpired(cmd="claude", timeout=5),
            subprocess.TimeoutExpired(cmd="claude", timeout=5),
            subprocess.TimeoutExpired(cmd="claude", timeout=5),
        ],
    ) as calls, mock.patch.object(
        llm, "emit_llm_call", side_effect=lambda **kw: emitted.append(kw)
    ), mock.patch.object(llm.time, "sleep"):
        try:
            llm.run_with_fallback(
                _calls(),
                timeout=5,
                max_attempts=3,
                allow_fallback=False,
            )
            raise AssertionError("exhaustion must fail closed")
        except llm.AllProvidersThrottled:
            pass
    assert calls.call_count == 3
    assert [event["provider"] for event in emitted] == ["claude"] * 3
    assert [event["status"] for event in emitted] == ["unavailable"] * 3
    print("ok: same-provider exhaustion -> hard stop, no sibling fallback")


def test_failed_attempt_stdout_is_never_accepted_or_retried():
    emitted = []
    with mock.patch.object(
        llm.subprocess,
        "run",
        side_effect=[_proc(1, "plausible but invalid answer", ""), _proc(0, "later")],
    ) as calls, mock.patch.object(
        llm, "emit_llm_call", side_effect=lambda **kw: emitted.append(kw)
    ), mock.patch.object(llm.time, "sleep"):
        try:
            llm.run_with_fallback(
                _calls(),
                timeout=5,
                max_attempts=3,
                allow_fallback=False,
            )
            raise AssertionError("nonzero stdout must not become an answer")
        except llm.LLMCallError:
            pass
    assert calls.call_count == 1
    assert emitted[0]["status"] == "error"
    print("ok: failed stdout rejected without semantic retry")


def test_judge_uses_same_provider_retry_policy():
    emitted = []
    with mock.patch.object(
        llm.subprocess,
        "run",
        side_effect=[
            subprocess.TimeoutExpired(cmd="claude", timeout=5),
            _proc(0, '{"verdict":"pass","reason":"fixture"}'),
        ],
    ) as calls, mock.patch.object(
        llm, "emit_llm_call", side_effect=lambda **kw: emitted.append(kw)
    ), mock.patch.object(llm.time, "sleep"):
        result = grading.call_judge_cli(
            "fixture",
            "opus",
            timeout=5,
            telemetry_context={
                "same_provider_max_attempts": 3,
                "allow_fallback": False,
            },
        )
    assert '"verdict":"pass"' in result
    assert calls.call_count == 2
    assert [event["provider"] for event in emitted] == ["claude", "claude"]
    print("ok: judge transport uses same-provider retry policy")


def test_native_executor_disables_sibling_fallback():
    spec = SimpleNamespace(
        prompt_id="fixture",
        spec={
            "model": "sonnet",
            "executor": {
                "type": "claude_cli",
                "same_provider_max_attempts": 3,
                "allow_fallback": False,
            },
        },
    )
    with mock.patch.object(
        llm.subprocess,
        "run",
        side_effect=[
            subprocess.TimeoutExpired(cmd="claude", timeout=5),
            subprocess.TimeoutExpired(cmd="claude", timeout=5),
            subprocess.TimeoutExpired(cmd="claude", timeout=5),
            _proc(0, "forbidden sibling answer"),
        ],
    ) as calls, mock.patch.object(llm.time, "sleep"):
        try:
            runner.execute_case(
                spec,
                "system prompt",
                {"input": "fixture"},
                timeout=5,
            )
            raise AssertionError("native executor exhaustion must hard stop")
        except runner.Throttled:
            pass
    assert calls.call_count == 3
    assert all(call.args[0][0] == "claude" for call in calls.call_args_list)
    print("ok: native executor policy disables sibling fallback")


def test_command_executor_forwards_transport_policy():
    spec = SimpleNamespace(
        prompt_id="fixture",
        repo=Path("/tmp"),
        spec={
            "model": "sonnet",
            "params": {},
            "executor": {
                "type": "command",
                "argv": ["fixture-adapter"],
                "same_provider_max_attempts": 3,
                "allow_fallback": False,
            },
        },
    )
    with mock.patch.object(runner, "_run_cli", return_value="answer") as run:
        assert runner.execute_case(spec, "prompt", {"x": 1}) == "answer"
    payload = json.loads(run.call_args.args[1])
    assert payload["transport_policy"] == {
        "same_provider_max_attempts": 3,
        "allow_fallback": False,
    }
    assert run.call_args.kwargs["max_attempts"] == 1
    print("ok: command executor forwards strict transport policy")


def test_command_executor_semantic_error_is_not_retried():
    with mock.patch.object(
        runner.subprocess,
        "run",
        side_effect=[
            _proc(1, "plausible but invalid", "schema error"),
            _proc(0, "later answer"),
        ],
    ) as calls:
        try:
            runner._run_cli(
                ["fixture-adapter"],
                stdin_text="{}",
                timeout=5,
                max_attempts=3,
            )
            raise AssertionError("semantic command failure must hard stop")
        except runner.RunError:
            pass
    assert calls.call_count == 1
    print("ok: command semantic error is not retried")


def test_judge_internal_typeerror_does_not_drop_policy_and_retry():
    calls = []

    def broken(prompt, model, telemetry_context=None):
        calls.append(telemetry_context)
        raise TypeError("internal caller bug")

    try:
        grading.run_judge_check(
            {"kind": "judge", "failure_mode": "fixture", "rubric": "fixture"},
            {"input": "fixture"},
            "output",
            "opus",
            caller=broken,
            telemetry_context={"allow_fallback": False},
        )
        raise AssertionError("internal TypeError must propagate")
    except TypeError as exc:
        assert "internal caller bug" in str(exc)
    assert calls == [{"allow_fallback": False}]
    print("ok: caller TypeError cannot trigger a policy-dropping retry")


def test_judge_circuit_and_transport_policy_reach_shared_transport():
    policy = {
        "same_provider_max_attempts": 3,
        "allow_fallback": False,
        "circuit": {"threshold": 7},
    }
    with mock.patch.object(
        grading, "run_with_fallback", return_value='{"verdict":"pass"}'
    ) as run:
        grading.call_judge_cli(
            "fixture",
            "opus",
            timeout=5,
            telemetry_context=policy,
        )
    assert run.call_args.kwargs["max_attempts"] == 3
    assert run.call_args.kwargs["allow_fallback"] is False
    assert run.call_args.kwargs["circuit_config"] == {"threshold": 7}
    print("ok: judge circuit and transport policy reach shared transport")


def test_transport_policy_rejects_truthy_strings_and_unbounded_attempts():
    invalid = [
        {"allow_fallback": "false"},
        {"same_provider_max_attempts": None},
        {"same_provider_max_attempts": 0},
        {"same_provider_max_attempts": 4},
    ]
    for policy in invalid:
        try:
            llm.transport_policy(policy)
            raise AssertionError(f"invalid policy accepted: {policy}")
        except llm.LLMCallError:
            pass
    print("ok: transport policy rejects coercions and unbounded attempts")


TESTS = [
    test_all_providers_unavailable_hard_stops,
    test_command_executor_forwards_transport_policy,
    test_command_executor_semantic_error_is_not_retried,
    test_empty_output_falls_back_and_is_not_success,
    test_expired_auth_falls_back_and_is_not_semantic,
    test_executor_empty_output_is_truthful_error,
    test_executor_nonempty_output_returns,
    test_failed_attempt_stdout_is_never_accepted_or_retried,
    test_judge_uses_same_provider_retry_policy,
    test_judge_circuit_and_transport_policy_reach_shared_transport,
    test_judge_internal_typeerror_does_not_drop_policy_and_retry,
    test_native_executor_disables_sibling_fallback,
    test_one_transient_timeout_recovers_on_same_provider,
    test_same_provider_exhaustion_fails_closed_without_fallback,
    test_semantic_error_is_fail_closed,
    test_throttle_still_falls_back,
    test_timeout_falls_back_to_sibling,
    test_transport_policy_rejects_truthy_strings_and_unbounded_attempts,
    test_two_transient_empty_results_recover_on_same_provider,
]


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
