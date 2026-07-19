"""Durable provider-availability circuit breaker for the subscription-CLI harness.

Problem it solves: once a provider (e.g. the Claude CLI) starts timing out on
every case, the plain fallback still pays that provider's full timeout on each
case before routing to the sibling. The breaker remembers the provider is
unhealthy and skips it for a cooldown, so the sibling is used immediately.

State machine, per provider:

    closed ──(≥THRESHOLD consecutive capacity failures)──► open
      ▲                                                     │
      │ success / (cooldown not elapsed → skip)             │ cooldown elapsed
      │                                                     ▼
    closed ◄──(probe succeeds)── half_open ──(probe fails)──► open
                                    │  (concurrent callers during a probe skip)

Rules:
  - Only capacity/availability failures count: timeout, throttle, empty output.
    Semantic errors NEVER open the circuit (the caller leaves it untouched).
  - A single HALF_OPEN probe is allowed after cooldown; others skip until it
    resolves (or its grace deadline lapses, guarding against a dead prober).
  - Success closes the circuit and resets the failure count.
  - State lives under runtime (never git). Every state/telemetry operation is
    best-effort: a failure to read/write state must never block a real call
    (ADR-0043 nonblocking) — the breaker degrades to "always attempt".

Persisted state is re-read on every call, so it survives process restarts with
no in-memory caching.
"""

from __future__ import annotations

import contextlib
import fcntl
import json
import os
import time
from pathlib import Path

from .core import TELEMETRY_PATH, append_jsonl, epoch_ms

STATE_FILE = Path(os.environ.get(
    "PROMPTEVAL_CIRCUIT_FILE",
    "/opt/workspace/runtime/.prompteval/circuit-breaker.json"))
THRESHOLD = int(os.environ.get("PROMPTEVAL_CIRCUIT_THRESHOLD", "3"))
COOLDOWN_S = float(os.environ.get("PROMPTEVAL_CIRCUIT_COOLDOWN", "120"))
PROBE_GRACE_S = float(os.environ.get("PROMPTEVAL_CIRCUIT_PROBE_GRACE", "60"))

# Injectable clock so tests are deterministic (monkeypatch circuit.now).
def now() -> float:
    return time.time()


def _default_rec():
    return {"state": "closed", "consecutive_failures": 0,
            "opened_at": 0.0, "cooldown_until": 0.0, "probe_deadline": 0.0,
            "last_reason": "", "last_model": ""}


@contextlib.contextmanager
def _lock():
    """Exclusive advisory lock over the state file. Yields True while held, or
    None if the lock can't be acquired (degrade to no-op — never block a call)."""
    lockf = None
    try:
        STATE_FILE.parent.mkdir(parents=True, exist_ok=True)
        lockf = open(str(STATE_FILE) + ".lock", "w")
        fcntl.flock(lockf, fcntl.LOCK_EX)
        yield True
    except OSError:
        yield None
    finally:
        if lockf is not None:
            try:
                fcntl.flock(lockf, fcntl.LOCK_UN)
            except OSError:
                pass
            lockf.close()


def _load():
    try:
        with STATE_FILE.open() as fh:
            data = json.load(fh)
        if isinstance(data, dict) and isinstance(data.get("providers"), dict):
            return data
    except (OSError, json.JSONDecodeError):
        pass
    return {"version": 1, "providers": {}}


def _save(data):
    tmp = STATE_FILE.with_suffix(f".{os.getpid()}.tmp")
    with tmp.open("w") as fh:
        json.dump(data, fh, indent=2, sort_keys=True)
        fh.write("\n")
    tmp.replace(STATE_FILE)


def _emit(event, provider, model, reason):
    try:
        append_jsonl(TELEMETRY_PATH, {
            "project": "prompteval",
            "source": "circuit-breaker",
            "eventType": event,  # circuit_open | circuit_skip | circuit_half_open | circuit_close
            "level": "warn" if event in ("circuit_open", "circuit_skip") else "info",
            "timestamp": epoch_ms(),
            "sourceType": "system",
            "provider": provider,
            "model": model,
            "reason": reason,
            "note": f"{event} {provider}/{model} {reason}"[:400],
        })
    except Exception:
        # telemetry is best-effort; never block execution
        pass


def allow(provider: str, model: str = "") -> str:
    """Decide whether to attempt `provider` now.

    Returns "attempt" (call it), "skip" (circuit open, go to sibling), or
    "probe" (half-open single trial). Best-effort: on any state error, "attempt".
    """
    t = now()
    try:
        with _lock() as held:
            if not held:
                return "attempt"
            data = _load()
            rec = data["providers"].get(provider) or _default_rec()
            st = rec.get("state", "closed")
            decision = "attempt"
            if st == "open":
                if t >= rec.get("cooldown_until", 0.0):
                    rec["state"] = "half_open"
                    rec["probe_deadline"] = t + PROBE_GRACE_S
                    decision = "probe"
                    _emit("circuit_half_open", provider,
                          rec.get("last_model") or model, rec.get("last_reason") or "")
                else:
                    decision = "skip"
                    _emit("circuit_skip", provider, model, rec.get("last_reason") or "cooldown")
            elif st == "half_open":
                if t >= rec.get("probe_deadline", 0.0):
                    # prior probe never resolved (crash/stall) — take over the probe
                    rec["probe_deadline"] = t + PROBE_GRACE_S
                    decision = "probe"
                    _emit("circuit_half_open", provider,
                          rec.get("last_model") or model, rec.get("last_reason") or "")
                else:
                    decision = "skip"
                    _emit("circuit_skip", provider, model, rec.get("last_reason") or "probing")
            data["providers"][provider] = rec
            _save(data)
            return decision
    except Exception:
        return "attempt"


def record_failure(provider: str, model: str, reason: str) -> None:
    """A capacity/availability failure (timeout | throttle | empty). May open."""
    t = now()
    try:
        with _lock() as held:
            if not held:
                return
            data = _load()
            rec = data["providers"].get(provider) or _default_rec()
            rec["consecutive_failures"] = int(rec.get("consecutive_failures", 0)) + 1
            rec["last_reason"] = reason
            rec["last_model"] = model
            was_open = rec.get("state") == "open"
            if rec.get("state") == "half_open" or rec["consecutive_failures"] >= THRESHOLD:
                rec["state"] = "open"
                rec["opened_at"] = t
                rec["cooldown_until"] = t + COOLDOWN_S
                rec["probe_deadline"] = 0.0
                if not was_open:
                    _emit("circuit_open", provider, model, reason)
            data["providers"][provider] = rec
            _save(data)
    except Exception:
        pass


def record_success(provider: str, model: str = "") -> None:
    """A real result. Closes the circuit and resets the failure count."""
    try:
        with _lock() as held:
            if not held:
                return
            data = _load()
            rec = data["providers"].get(provider)
            if not rec:
                return  # provider never failed; nothing to reset
            if rec.get("state") != "closed" or rec.get("consecutive_failures"):
                if rec.get("state") in ("open", "half_open"):
                    _emit("circuit_close", provider, model, "success")
                data["providers"][provider] = _default_rec()
                _save(data)
    except Exception:
        pass
