"""Subscription-CLI LLM calls: fallback, throttling, and per-call telemetry."""

from __future__ import annotations

import math
import re
import subprocess
import time
from dataclasses import dataclass

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


class AllProvidersThrottled(Exception):
    def __init__(self, throttles: list[ProviderThrottled]):
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
            status = "timeout"
            detail = f"timed out after {timeout}s"
            raise LLMCallError(detail) from exc
        finally:
            latency_ms = int((time.monotonic() - started) * 1000)
            if exit_code == 0:
                status = "success"
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
            return stdout
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
) -> str:
    throttles: list[ProviderThrottled] = []
    for call in calls:
        try:
            return run_cli_call(
                call,
                timeout=timeout,
                retries=retries,
                role=role,
                project=project,
                prompt_id=prompt_id,
                case_id=case_id,
                trial=trial,
            )
        except ProviderThrottled as exc:
            throttles.append(exc)
            continue
    if throttles:
        raise AllProvidersThrottled(throttles)
    raise LLMCallError("no provider calls configured")
