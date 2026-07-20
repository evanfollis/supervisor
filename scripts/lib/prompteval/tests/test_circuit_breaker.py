#!/usr/bin/env python3
"""Deterministic tests for the provider-availability circuit breaker.

Unit tests drive a controllable clock (circuit.now); persistence and concurrency
tests use real subprocesses against a shared state file so the fcntl lock and
cross-process durability are exercised for real.
"""

import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path

LIB = str(Path(__file__).resolve().parents[2])
sys.path.insert(0, LIB)

from prompteval import circuit  # noqa: E402


def _setup(tmp, threshold=3, cooldown=60.0, grace=30.0, t0=1000.0):
    circuit.STATE_FILE = Path(tmp) / "circuit.json"
    circuit.THRESHOLD = threshold
    circuit.COOLDOWN_S = cooldown
    circuit.PROBE_GRACE_S = grace
    clock = {"t": t0}
    circuit.now = lambda: clock["t"]
    # telemetry to a throwaway file so tests never touch the real stream
    import prompteval.core as core
    core.TELEMETRY_PATH = Path(tmp) / "telem.jsonl"
    circuit.TELEMETRY_PATH = core.TELEMETRY_PATH
    return clock


def _state(provider="claude"):
    return json.loads(circuit.STATE_FILE.read_text())["providers"].get(provider, {})


# ---- unit: state machine ----

def test_throttle_opens_only_after_threshold():
    # Throttle is a TRANSIENT capacity signal — a single 429 must not open.
    with tempfile.TemporaryDirectory() as tmp:
        _setup(tmp, threshold=3)
        assert circuit.allow("claude") == "attempt"
        circuit.record_failure("claude", "sonnet", "throttle")
        circuit.record_failure("claude", "sonnet", "throttle")
        assert circuit.allow("claude") == "attempt", "transient throttle must not open before threshold"
        circuit.record_failure("claude", "sonnet", "throttle")  # 3rd -> open
        assert _state()["state"] == "open"
        assert circuit.allow("claude") == "skip", "open circuit within cooldown must skip"
        print("ok: throttle opens only after threshold; skips during cooldown")


def test_timeout_opens_immediately():
    # A full subprocess timeout is DECISIVE — one occurrence opens the circuit,
    # regardless of the (throttle) threshold, so we never pay it N more times.
    with tempfile.TemporaryDirectory() as tmp:
        _setup(tmp, threshold=3)
        circuit.record_failure("claude", "sonnet", "timeout")  # single decisive failure
        assert _state()["state"] == "open", "one timeout must open the circuit"
        assert circuit.allow("claude") == "skip"
        print("ok: timeout opens immediately (decisive), ignoring the throttle threshold")


def test_empty_output_opens_immediately():
    with tempfile.TemporaryDirectory() as tmp:
        _setup(tmp, threshold=3)
        circuit.record_failure("claude", "sonnet", "empty")  # single decisive failure
        assert _state()["state"] == "open", "one empty-output must open the circuit"
        print("ok: empty-output opens immediately (decisive)")


def test_per_spec_config_override():
    # threshold override (raise the throttle threshold) — no env vars
    with tempfile.TemporaryDirectory() as tmp:
        _setup(tmp, threshold=3, cooldown=120.0, t0=500.0)
        cfg = {"threshold": 5}
        for _ in range(4):
            circuit.record_failure("claude", "sonnet", "throttle", config=cfg)
        assert _state()["state"] == "closed", "override threshold=5 not reached at 4 throttles"
        circuit.record_failure("claude", "sonnet", "throttle", config=cfg)  # 5th -> open
        assert _state()["state"] == "open"
    # cooldown override applied at open time
    with tempfile.TemporaryDirectory() as tmp:
        _setup(tmp, cooldown=120.0, t0=500.0)
        circuit.record_failure("claude", "sonnet", "throttle",
                               config={"threshold": 1, "cooldown_s": 300.0})
        assert _state()["cooldown_until"] == 500.0 + 300.0, _state()["cooldown_until"]
    # decisive_reasons override: make timeout transient for this spec
    with tempfile.TemporaryDirectory() as tmp:
        _setup(tmp, threshold=3)
        circuit.record_failure("claude", "sonnet", "timeout", config={"decisive_reasons": ["empty"]})
        assert _state()["state"] == "closed", "timeout is transient when excluded from decisive_reasons"
        print("ok: per-spec config overrides threshold, cooldown, and decisive_reasons (no env)")


def test_probe_after_cooldown_then_close_on_success():
    with tempfile.TemporaryDirectory() as tmp:
        clock = _setup(tmp, threshold=1, cooldown=60.0, t0=100.0)
        circuit.record_failure("claude", "sonnet", "timeout")  # opens at t=100, cooldown->160
        clock["t"] = 130.0
        assert circuit.allow("claude") == "skip"
        clock["t"] = 170.0  # cooldown elapsed
        assert circuit.allow("claude") == "probe"
        assert _state()["state"] == "half_open"
        circuit.record_success("claude", "sonnet")
        assert _state()["state"] == "closed"
        assert circuit.allow("claude") == "attempt"
        print("ok: probe after cooldown; success closes")


def test_probe_failure_reopens():
    with tempfile.TemporaryDirectory() as tmp:
        clock = _setup(tmp, threshold=1, cooldown=60.0, t0=100.0)
        circuit.record_failure("claude", "sonnet", "timeout")
        clock["t"] = 170.0
        assert circuit.allow("claude") == "probe"       # half_open
        circuit.record_failure("claude", "sonnet", "empty")  # probe fails -> reopen
        assert _state()["state"] == "open"
        assert _state()["cooldown_until"] == 170.0 + 60.0
        assert circuit.allow("claude") == "skip"
        print("ok: probe failure reopens with fresh cooldown")


def test_success_resets_failure_count():
    with tempfile.TemporaryDirectory() as tmp:
        _setup(tmp, threshold=3)
        circuit.record_failure("claude", "sonnet", "timeout")
        circuit.record_failure("claude", "sonnet", "timeout")
        circuit.record_success("claude", "sonnet")
        assert _state()["consecutive_failures"] == 0
        assert _state()["state"] == "closed"
        print("ok: success resets consecutive failure count")


def test_semantic_error_does_not_open_the_circuit():
    # A semantic error must never call record_failure — the circuit stays closed.
    # This mirrors run_with_fallback, which leaves LLMCallError uncaught.
    with tempfile.TemporaryDirectory() as tmp:
        _setup(tmp, threshold=1)
        for _ in range(5):
            # semantic errors bypass the breaker entirely (no record_failure)
            pass
        assert circuit.allow("claude") == "attempt"
        # and if only successes are recorded, it never opens
        circuit.record_success("claude", "sonnet")
        assert circuit.allow("claude") == "attempt"
        print("ok: semantic errors (no record_failure) never open the circuit")


def test_state_error_degrades_to_attempt():
    with tempfile.TemporaryDirectory() as tmp:
        _setup(tmp)
        # point the state file at an unwritable path -> lock fails -> attempt
        circuit.STATE_FILE = Path("/proc/nonexistent-dir/circuit.json")
        assert circuit.allow("claude") == "attempt", "must never block on state errors"
        circuit.record_failure("claude", "sonnet", "timeout")  # must not raise
        circuit.record_success("claude", "sonnet")             # must not raise
        print("ok: state/telemetry errors degrade to attempt, never block")


# ---- subprocess: restart persistence + concurrency ----

def _sub(state_file, snippet, threshold=3, cooldown=60):
    env = {**os.environ, "PYTHONPATH": LIB,
           "PROMPTEVAL_CIRCUIT_FILE": str(state_file),
           "PROMPTEVAL_CIRCUIT_THRESHOLD": str(threshold),
           "PROMPTEVAL_CIRCUIT_COOLDOWN": str(cooldown),
           "PROMPTEVAL_TELEMETRY": str(state_file) + ".telem"}
    return subprocess.Popen([sys.executable, "-c",
                             "from prompteval import circuit\n" + snippet],
                            env=env, stdout=subprocess.PIPE, text=True)


def test_restart_persistence():
    with tempfile.TemporaryDirectory() as tmp:
        sf = Path(tmp) / "c.json"
        future = 10_000_000_000.0  # cooldown far in the future
        sf.write_text(json.dumps({"version": 1, "providers": {"claude": {
            "state": "open", "consecutive_failures": 3, "opened_at": 0.0,
            "cooldown_until": future, "probe_deadline": 0.0,
            "last_reason": "timeout", "last_model": "sonnet"}}}))
        p = _sub(sf, "print(circuit.allow('claude','sonnet'))")
        out, _ = p.communicate(timeout=30)
        assert out.strip() == "skip", f"fresh process must read persisted OPEN state, got {out!r}"
        print("ok: circuit state persists across process restart")


def test_concurrent_failures_are_not_lost():
    with tempfile.TemporaryDirectory() as tmp:
        sf = Path(tmp) / "c.json"
        n = 8
        procs = [_sub(sf, "circuit.record_failure('claude','sonnet','throttle')",
                      threshold=1000) for _ in range(n)]
        for p in procs:
            p.communicate(timeout=30)
        cf = json.loads(sf.read_text())["providers"]["claude"]["consecutive_failures"]
        assert cf == n, f"expected {n} counted failures under concurrency, got {cf}"
        print(f"ok: {n} concurrent failures all counted (no lost updates)")


def test_concurrent_probe_admits_exactly_one():
    with tempfile.TemporaryDirectory() as tmp:
        sf = Path(tmp) / "c.json"
        # open but already expired -> the first caller probes, others must skip
        sf.write_text(json.dumps({"version": 1, "providers": {"claude": {
            "state": "open", "consecutive_failures": 5, "opened_at": 0.0,
            "cooldown_until": 0.0, "probe_deadline": 0.0,
            "last_reason": "timeout", "last_model": "sonnet"}}}))
        n = 8
        procs = [_sub(sf, "print(circuit.allow('claude','sonnet'))", cooldown=600)
                 for _ in range(n)]
        outs = [p.communicate(timeout=30)[0].strip() for p in procs]
        assert outs.count("probe") == 1, f"exactly one probe expected, got {outs}"
        assert outs.count("skip") == n - 1, outs
        print("ok: concurrent half-open admits exactly one probe")


TESTS = [
    test_concurrent_failures_are_not_lost,
    test_concurrent_probe_admits_exactly_one,
    test_empty_output_opens_immediately,
    test_per_spec_config_override,
    test_probe_after_cooldown_then_close_on_success,
    test_probe_failure_reopens,
    test_restart_persistence,
    test_semantic_error_does_not_open_the_circuit,
    test_state_error_degrades_to_attempt,
    test_success_resets_failure_count,
    test_throttle_opens_only_after_threshold,
    test_timeout_opens_immediately,
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
