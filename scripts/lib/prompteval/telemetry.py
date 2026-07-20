"""Typed telemetry events per the workspace contract (S1-P2, ADR-0029).

Event shape: { project, source, eventType, level, timestamp, sourceType,
note, ref } — timestamp is epoch milliseconds (integer). eventType
distinguishes real failures from designed throttling (S1-P2 addendum);
"escalated" is reserved for self-reported stuck states (S3-P2).
"""

from __future__ import annotations

import json
import os
from pathlib import Path

from .core import TELEMETRY_PATH, append_jsonl, epoch_ms

EVENT_TYPES = {"info", "failure", "throttled", "escalated", "llm_call"}


def emit_llm_transcript(
    *,
    run_id: str,
    project: str,
    prompt_id: str,
    case_id: str,
    trial: int | None,
    role: str,
    provider: str,
    model: str,
    status: str,
    attempt: int,
    fallback_from: str,
    input_text: str,
    output_text: str,
    stderr_text: str,
    detail: str,
) -> None:
    """Append a private, run-scoped full transcript outside aggregate telemetry."""
    if not run_id:
        return
    try:
        root = Path(os.environ.get(
            "PROMPTEVAL_RUNTIME",
            "/opt/workspace/runtime/prompteval",
        )) / ".transcripts"
        root.mkdir(parents=True, exist_ok=True, mode=0o700)
        os.chmod(root, 0o700)
        path = root / f"{run_id}.jsonl"
        payload = {
            "timestamp": epoch_ms(),
            "runId": run_id,
            "project": project,
            "promptId": prompt_id,
            "caseId": case_id,
            "trial": trial,
            "role": role,
            "provider": provider,
            "model": model,
            "status": status,
            "attempt": attempt,
            "fallbackFrom": fallback_from,
            "input": input_text,
            "output": output_text,
            "stderr": stderr_text,
            "detail": detail,
        }
        encoded = (json.dumps(
            payload,
            sort_keys=True,
            separators=(",", ":"),
            ensure_ascii=False,
        ) + "\n").encode("utf-8")
        fd = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_APPEND, 0o600)
        try:
            remaining = memoryview(encoded)
            while remaining:
                remaining = remaining[os.write(fd, remaining):]
        finally:
            os.close(fd)
        os.chmod(path, 0o600)
    except OSError:
        # Transcript capture is secondary evidence and must never block the gate.
        pass


def emit(
    project: str,
    event_type: str,
    note: str,
    ref: str = "",
    source_type: str = "system",
    level: str = "info",
) -> None:
    if event_type not in EVENT_TYPES:
        event_type = "info"
    try:
        append_jsonl(
            TELEMETRY_PATH,
            {
                "project": project,
                "source": "prompteval",
                "eventType": event_type,
                "level": level,
                "timestamp": epoch_ms(),
                "sourceType": source_type,
                "note": note[:400],
                "ref": ref,
            },
        )
    except OSError:
        # Telemetry must never take down the gate; the gate's own output
        # is the primary channel, events are the secondary one.
        pass


def emit_llm_call(
    project: str,
    prompt_id: str,
    role: str,
    provider: str,
    model: str,
    status: str,
    latency_ms: int,
    input_chars: int,
    output_chars: int,
    input_tokens: int,
    output_tokens: int,
    token_source: str,
    case_id: str = "",
    trial: int | None = None,
    attempt: int | None = None,
    fallback_from: str = "",
    exit_code: int | None = None,
    detail: str = "",
    run_id: str = "",
) -> None:
    event = {
        "project": project,
        "source": "prompteval",
        "eventType": "llm_call",
        "level": "info" if status == "success" else "warn",
        "timestamp": epoch_ms(),
        "sourceType": "system",
        "note": f"{role} {provider}/{model} {status}"[:400],
        "ref": prompt_id,
        "promptId": prompt_id,
        "runId": run_id,
        "caseId": case_id,
        "trial": trial,
        "role": role,
        "provider": provider,
        "model": model,
        "status": status,
        "latencyMs": latency_ms,
        "inputChars": input_chars,
        "outputChars": output_chars,
        "inputTokens": input_tokens,
        "outputTokens": output_tokens,
        "totalTokens": input_tokens + output_tokens,
        "tokenSource": token_source,
        "attempt": attempt,
        "fallbackFrom": fallback_from,
        "exitCode": exit_code,
        "detail": detail[:800],
    }
    try:
        append_jsonl(TELEMETRY_PATH, event)
    except OSError:
        pass
    if run_id:
        try:
            provenance_root = Path(os.environ.get(
                "PROMPTEVAL_RUNTIME",
                "/opt/workspace/runtime/prompteval",
            )) / ".provenance"
            append_jsonl(provenance_root / f"{run_id}.jsonl", event)
        except OSError:
            pass
