"""Subscription-CLI LLM calls: fallback, throttling, and per-call telemetry."""

from __future__ import annotations

import math
import re
import subprocess
import time
from contextvars import ContextVar, Token
from dataclasses import dataclass

from . import circuit
from .telemetry import emit_llm_call, emit_llm_transcript

THROTTLE_RE = re.compile(
    r"rate.?limit|overloaded|429|usage limit|session limit|hit your .*limit",
    re.IGNORECASE,
)
AUTH_UNAVAILABLE_RE = re.compile(
    r"failed to authenticate|oauth session expired|could not be refreshed|"
    r"not logged in|authentication required",
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


MAX_SAME_PROVIDER_ATTEMPTS = 3


def transport_policy(config: dict | None) -> tuple[int, bool]:
    """Validate bounded retry/fallback policy without truthiness coercions."""
    config = config or {}
    max_attempts = config.get("same_provider_max_attempts", 2)
    allow_fallback = config.get("allow_fallback", True)
    if (
        type(max_attempts) is not int
        or not 1 <= max_attempts <= MAX_SAME_PROVIDER_ATTEMPTS
    ):
        raise LLMCallError(
            "same_provider_max_attempts must be an integer between "
            f"1 and {MAX_SAME_PROVIDER_ATTEMPTS}"
        )
    if type(allow_fallback) is not bool:
        raise LLMCallError("allow_fallback must be a boolean")
    return max_attempts, allow_fallback


# A run-scoped metadata channel keeps provider provenance coupled to the
# evaluator that produced it without threading bookkeeping arguments through
# every adapter and grader call. ContextVar keeps the mechanism safe if the
# harness later gains concurrency; only non-content metadata is retained here.
_RUN_PROVENANCE: ContextVar[dict | None] = ContextVar(
    "prompteval_run_provenance", default=None
)


def begin_run_provenance(run_id: str) -> tuple[Token, dict]:
    state = {"run_id": run_id}
    return _RUN_PROVENANCE.set(state), state


def end_run_provenance(token: Token) -> None:
    _RUN_PROVENANCE.reset(token)


def current_run_id() -> str:
    state = _RUN_PROVENANCE.get()
    return str((state or {}).get("run_id") or "")


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


def is_auth_unavailable(text: str) -> bool:
    """Return true when the subscription CLI cannot currently authenticate.

    Authentication transport failures are provider unavailability, not a
    semantic failure in the evaluated prompt. Treating them as semantic errors
    incorrectly suppresses an explicitly authorized sibling-provider fallback.
    """
    return bool(AUTH_UNAVAILABLE_RE.search(text or ""))


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
    max_attempts: int = 2,
    role: str = "executor",
    project: str = "",
    prompt_id: str = "",
    case_id: str = "",
    trial: int | None = None,
    run_id: str = "",
) -> str:
    if (
        type(max_attempts) is not int
        or not 1 <= max_attempts <= MAX_SAME_PROVIDER_ATTEMPTS
    ):
        raise LLMCallError(
            "max_attempts must be an integer between "
            f"1 and {MAX_SAME_PROVIDER_ATTEMPTS}"
        )
    for attempt in range(max_attempts):
        started = time.monotonic()
        status = "error"
        exit_code = None
        stdout = ""
        stderr = ""
        detail = ""
        availability_error: ProviderUnavailable | None = None
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
            availability_error = ProviderUnavailable(
                call.provider, detail, kind="timeout"
            )
        finally:
            latency_ms = int((time.monotonic() - started) * 1000)
            resolved_run_id = run_id or current_run_id()
            if exit_code == 0:
                # Exit 0 with empty/whitespace output is NOT success — the
                # provider ran but produced nothing (the "Claude returned empty"
                # failure). Record it truthfully so it can't read as a clean run.
                status = "success" if (stdout or "").strip() else "empty"
            elif exit_code is not None:
                diag = ((stderr or "").strip() or (stdout or "").strip())[-800:]
                if is_throttle(diag):
                    status = "throttled"
                elif is_auth_unavailable(diag):
                    status = "unavailable"
                else:
                    status = "error"
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
                run_id=resolved_run_id,
            )
            emit_llm_transcript(
                run_id=resolved_run_id,
                project=project,
                prompt_id=prompt_id,
                case_id=case_id,
                trial=trial,
                role=role,
                provider=call.provider,
                model=call.model or "default",
                status=status,
                attempt=attempt + 1,
                fallback_from=call.fallback_from,
                input_text=call.input_text or call.stdin_text or "",
                output_text=stdout,
                stderr_text=stderr,
                detail=detail,
            )
        if availability_error is not None:
            if attempt + 1 < max_attempts:
                time.sleep(5)
                continue
            raise availability_error
        if exit_code == 0:
            if (stdout or "").strip():
                return stdout
            # Exit 0 but empty output is a transport/availability failure, not
            # a semantic answer. Retry only this exact provider/model before
            # the caller decides whether any sibling is allowed.
            availability_error = ProviderUnavailable(
                call.provider, "exit 0 with empty output", kind="empty"
            )
            if attempt + 1 < max_attempts:
                time.sleep(5)
                continue
            raise availability_error
        diag = ((stderr or "").strip() or (stdout or "").strip())[-800:]
        if is_throttle(diag):
            raise ProviderThrottled(call.provider, diag)
        if is_auth_unavailable(diag):
            # Retrying the same expired OAuth session cannot recover without
            # external reauthentication. Surface provider unavailability now
            # so the caller can use an explicitly allowed sibling provider.
            raise ProviderUnavailable(call.provider, diag, kind="auth")
        # A nonzero non-throttle result is semantic/command failure. Never
        # retry it and never accept stdout from it as a later answer.
        raise LLMCallError(
            f"{call.provider} exited {exit_code}: {diag or '<no output>'}"
        )


def run_with_fallback(
    calls: list[CliCall],
    timeout: int,
    max_attempts: int = 2,
    allow_fallback: bool = True,
    role: str = "executor",
    project: str = "",
    prompt_id: str = "",
    case_id: str = "",
    trial: int | None = None,
    circuit_config: dict | None = None,
    run_id: str = "",
) -> str:
    unavailable: list[ProviderThrottled | ProviderUnavailable] = []
    eligible_calls = calls if allow_fallback else calls[:1]
    for call in eligible_calls:
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
                max_attempts=max_attempts,
                role=role,
                project=project,
                prompt_id=prompt_id,
                case_id=case_id,
                trial=trial,
                run_id=run_id,
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
