# Events

Append-only log of supervisor actions. One file: `supervisor-events.jsonl`.

## Purpose

Telemetry on the supervisor itself — what it did, when, and why. Enables:

- Post-hoc review ("what happened during last week's chaos?")
- Reflection loop input (the supervisor's own reflections can read these)
- Detecting loops, thrash, or ignored handoffs

## Event shape

One JSON object per line:

```json
{
  "ts": "2026-04-14T14:55:00Z",
  "agent": "claude",
  "type": "handoff_received",
  "ref": "handoffs/INBOX/2026-04-13T22-00-foo.md",
  "note": "Acted on kalman-filter feature branch merge"
}
```

## Required fields

- `ts` — ISO-8601 UTC timestamp
- `agent` — `claude` or `codex`
- `type` — see list in `AGENT.md` § Event model
- `ref` — path or ID of the artifact this event references
- `note` — single-line human-readable summary (≤120 chars)

## Optional fields

- `trigger` — what caused this action (`scheduled`, `handoff`, `user`, `synthesis`)
- `downstream` — array of paths/IDs this event resulted in

## Rules

- **Append-only.** Never edit past entries.
- **Write before acting.** Emit `delegated` before creating the handoff file, not after. Makes replay robust to mid-action crashes.
- **One line per event.** Don't pretty-print.
