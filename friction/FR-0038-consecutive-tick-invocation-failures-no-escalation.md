---
id: FR-0038
name: Consecutive tick claude invocation failures produced no escalated event
created: 2026-04-29T02:49Z
source: supervisor-tick-2026-04-29T02-49-55Z
severity: high
status: open
---

# FR-0038: Consecutive tick invocation failures — no escalated event emitted

## What happened

The supervisor tick at 16:49Z and 18:48Z on 2026-04-28 both logged `"tick claude invocation failed"` in the events journal. Two consecutive failures occurred with no `escalated` event emitted and no URGENT handoff written to INBOX.

CLAUDE.md requires: "Any automated loop must emit a named `escalated` event after N consecutive skips or silent failures. The threshold for the tick is 3 consecutive same-reason skips."

These were 2 consecutive failures (below the 3-failure threshold for `escalated`), but:
- No `escalated` event was emitted at any threshold
- No URGENT was written even after the 2nd consecutive failure
- The pattern has recurred across multiple prior windows (cited in reflections since 2026-04-26)

## Root cause

The tick wrapper (`supervisor-tick.sh`) handles invocation failure by logging a `session_reflected` event with note "tick claude invocation failed" but does not:
1. Track consecutive failure count across runs
2. Emit `eventType: "escalated"` after threshold
3. Write URGENT INBOX item after 2+ consecutive failures

## Impact

- S3-P2 self-monitoring rule violated for the tick itself
- Failed ticks are indistinguishable from silent ticks in the events journal
- No escalation path to surface structural model-access problems

## Required fix

In `scripts/lib/supervisor-tick.sh` (or its wrapper):
- Track consecutive invocation failure count (e.g. `.meta/tick-consecutive-failures` counter file)
- On failure: increment counter; if count ≥ 3, emit `eventType: "escalated"` and write URGENT INBOX
- On success: reset counter

Tier C change — requires attended session.
