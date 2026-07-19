"""Subscription-CLI LLM calls: fallback, throttling, and per-call telemetry."""

from __future__ import annotations

import math
import re
import subprocess
import time
from dataclasses import dataclass

from . import circuit
from .telemetry import emit_llm_call

THROTTLE_RE = re.compile(
    r"rate.?limit|overloaded|429|usage limit|session limit|hit your .*limit",
    re.IGNORECASE,
)


class ProviderThrottled(Exception):
    def __init__(self, provider: str, detail: str):
        self.provider = provider
        self.detail = detail
        super().__init__(f"{provider}: {detail}")


class ProviderUnavailable(Exception):
    def __init__(self, provider: str, detail: str, kind: str = "unavailable"):
        self.provider = provider
        self.detail = detail
        self.kind = kind  # "timeout" | "empty" | "unavailable" — drives circuit policy
        super().__init__(f"{provider}: {detail}")


class AllProvidersThrottled(Exception):
    def __init__(self, throttles: list[ProviderThrottled | ProviderUnavailable]):
        self.throttles = throttles
        detail = " | ".join(f"{t.provider}: {t.detail}" for t in throttles)
        super().__init__("all providers blocked: " + detail)


class LLMCallError(Exception):
    pass


@dataclass
class CliCall:
    provider: str
    model: str
    cmd: list[str]
    stdin_text: str | None = None
    input_text: str = ""
    cwd: str | None = None
    fallback_from: str = ""
    # Per-provider circuit override (threshold / cooldown_s / probe_grace_s /
    # decisive_reasons). Lets a spec or adapter tune the breaker programmatically
    # without ad-hoc environment variables. None → module defaults.
    circuit_config: dict | None = None


def estimate_tokens(text: str | None) -> int:
    """Cheap, explicit estimate for CLIs that do not expose token accounting."""
    if not text:
        return 0
    return max(1, math.ceil(len(text) / 4))


def is_throttle(text: str) -> bool:
    return bool(THROTTLE_RE.search(text or ""))


def provider_for_model(model: str, default: str = "claude") -> str:
    m = (model or "").lower()
    if m.startswith(("gpt", "o1", "o3", "o4", "o5")) or "codex" in m:
        return "codex"
    if m.startswith("claude") or m in {"opus", "sonnet", "haiku"}:
        return "claude"
    return default


def fallback_model(provider: str, configured: str | None = None) -> str:
    if configured:
        return configured
    if provider == "claude":
        return "sonnet"
    return ""


def run_cli_call(
    call: CliCall,
    timeout: int,
    retries: int = 1,
    role: str = "executor",
    project: str = "",
    prompt_id: str = "",
    case_id: str = "",
    trial: int | None = None,
) -> str:
    last_err = ""
    for attempt in range(retries + 1):
        started = time.monotonic()
        status = "error"
        exit_code = None
        stdout = ""
        stderr = ""
        detail = ""
        try:
            proc = subprocess.run(
                call.cmd,
                input=call.stdin_text,
                capture_output=True,
                text=True,
                timeout=timeout,
                cwd=call.cwd,
                check=False,
            )
            exit_code = proc.returncode
            stdout = proc.stdout or ""
            stderr = proc.stderr or ""
        except FileNotFoundError as exc:
            detail = f"binary not found: {call.cmd[0]}"
            raise LLMCallError(detail) from exc
        except subprocess.TimeoutExpired as exc:
            # llm_call telemetry status stays "unavailable"; the precise kind
            # ("timeout") rides on the exception and drives circuit policy, and
            # the circuit's own event carries reason=timeout.
            status = "unavailable"
            detail = f"timed out after {timeout}s"
            raise ProviderUnavailable(call.provider, detail, kind="timeout") from exc
        finally:
            latency_ms = int((time.monotonic() - started) * 1000)
            if exit_code == 0:
                # Exit 0 with empty/whitespace output is NOT success — the
                # provider ran but produced nothing (the "Claude returned empty"
                # failure). Record it truthfully so it can't read as a clean run.
                status = "success" if (stdout or "").strip() else "empty"
            elif exit_code is not None:
                diag = ((stderr or "").strip() or (stdout or "").strip())[-800:]
                status = "throttled" if is_throttle(diag) else "error"
                detail = diag or "<no output>"
            emit_llm_call(
                project=project,
                prompt_id=prompt_id,
                role=role,
                provider=call.provider,
                model=call.model or "default",
                status=status,
                latency_ms=latency_ms,
                input_chars=len(call.input_text or call.stdin_text or ""),
                output_chars=len(stdout),
                input_tokens=estimate_tokens(call.input_text or call.stdin_text),
                output_tokens=estimate_tokens(stdout),
                token_source="estimated_chars_div_4",
                case_id=case_id,
                trial=trial,
                attempt=attempt + 1,
                fallback_from=call.fallback_from,
                exit_code=exit_code,
                detail=detail,
            )
        if exit_code == 0:
            if (stdout or "").strip():
                return stdout
            # Exit 0 but empty output: an availability failure, not a result.
            # Fall back to the sibling subscription CLI once (via run_with_fallback)
            # instead of returning "" as a falsely-successful answer.
            raise ProviderUnavailable(call.provider, "exit 0 with empty output", kind="empty")
        diag = ((stderr or "").strip() or (stdout or "").strip())[-800:]
        if is_throttle(diag):
            raise ProviderThrottled(call.provider, diag)
        last_err = f"{call.provider} exited {exit_code}: {diag or '<no output>'}"
        if attempt < retries:
            time.sleep(5)
    raise LLMCallError(last_err)


def run_with_fallback(
    calls: list[CliCall],
    timeout: int,
    retries: int = 1,
    role: str = "executor",
    project: str = "",
    prompt_id: str = "",
    case_id: str = "",
    trial: int | None = None,
    circuit_config: dict | None = None,
) -> str:
    unavailable: list[ProviderThrottled | ProviderUnavailable] = []
    for call in calls:
        model = call.model or "default"
        # Per-provider override (CliCall.circuit_config) beats the spec-level
        # default (circuit_config); either beats module defaults.
        cfg = call.circuit_config or circuit_config
        # Circuit breaker: skip a provider that is in cooldown so we don't pay
        # its timeout on every case. "probe" and "attempt" both make the call.
        if circuit.allow(call.provider, model, config=cfg) == "skip":
            unavailable.append(
                ProviderUnavailable(call.provider, "circuit open — skipped (cooldown)"))
            continue
        try:
            result = run_cli_call(
                call,
                timeout=timeout,
                retries=retries,
                role=role,
                project=project,
                prompt_id=prompt_id,
                case_id=case_id,
                trial=trial,
            )
        except (ProviderThrottled, ProviderUnavailable) as exc:
            # capacity/availability failure — counts toward opening the circuit.
            # Reason drives failure-kind policy: throttle is transient (threshold-
            # gated); timeout/empty are decisive (open on first occurrence).
            if isinstance(exc, ProviderThrottled):
                reason = "throttle"
            else:
                reason = getattr(exc, "kind", "unavailable")
            circuit.record_failure(call.provider, model, reason, config=cfg)
            unavailable.append(exc)
            continue
        # NOTE: LLMCallError (a semantic/non-capacity error) is intentionally not
        # caught here — it propagates fail-closed and leaves the circuit untouched
        # (semantic errors must never open the circuit, and must not fall back).
        circuit.record_success(call.provider, model, config=cfg)
        return result
    if unavailable:
        raise AllProvidersThrottled(unavailable)
    raise LLMCallError("no provider calls configured")
