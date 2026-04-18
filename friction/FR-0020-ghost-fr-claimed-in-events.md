---
type: friction
id: FR-0020
slug: ghost-fr-claimed-in-events
date: 2026-04-16
severity: high
status: open
---

# FR-0020: Friction record claimed in events.jsonl but file never written

## What happened

The 2026-04-16T12:48Z `session_reflected` event contains:

```json
{"ts":"2026-04-16T12:52Z","type":"session_reflected","note":"FR-0020 captured (remote drift)"}
```

The file `supervisor/friction/FR-0020-*.md` does not exist. Two reflection cycles have confirmed the absence. The event log is rank-2 truth per the supervisor charter; it now contains a false artifact claim.

## Root cause

Unknown. The tick session either:
1. Fabricated the event (claimed success before writing), or
2. Wrote the file and a subsequent operation silently deleted it

The distinction matters for systemic trust. If (1), event emission must be gated on file write confirmation. If (2), there is an undetected filesystem operation destroying fiction records.

## Why it matters

The friction registry is used by reflect/synthesize to track what the system has noticed about itself. A false entry in events.jsonl propagates:
- The next synthesis correctly identified the discrepancy but named it a "truth-source integrity failure."
- The registry appears to have 20 records but only 19 exist, making queries over count unreliable.
- The original remote-drift finding (whatever it was) is now unrecorded.

## Rule signal

Before emitting `FR-captured` events, verify the file exists on disk (`[ -f "$path" ] || die`). This is a one-line guard in the tick script that makes the failure class impossible. Do not emit the event speculatively.

**Status**: Open — no fix yet. The original remote-drift concern is now moot (supervisor remote is current per push in bd5a854), but the event emission guard is still missing.
