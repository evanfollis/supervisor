"""Typed telemetry events per the workspace contract (S1-P2, ADR-0029).

Event shape: { project, source, eventType, level, timestamp, sourceType,
note, ref } — timestamp is epoch milliseconds (integer). eventType
distinguishes real failures from designed throttling (S1-P2 addendum);
"escalated" is reserved for self-reported stuck states (S3-P2).
"""

from __future__ import annotations

from .core import TELEMETRY_PATH, append_jsonl, epoch_ms

EVENT_TYPES = {"info", "failure", "throttled", "escalated"}


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
