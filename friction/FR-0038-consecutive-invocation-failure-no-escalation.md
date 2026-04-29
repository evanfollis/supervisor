---
name: FR-0038 — Consecutive tick invocation failures with no S3-P2 escalation
status: Open
created: 2026-04-29T08:48Z
source: supervisor-tick-2026-04-29T08-48-55Z
---

# FR-0038 — Consecutive tick invocation failures with no S3-P2 escalation

## What happened

Tick cron at 04:49Z and 06:49Z UTC on 2026-04-29 both emitted `session_reflected`
events with "tick claude invocation failed" notes. Two consecutive same-reason
failures. The S3-P2 rule in workspace CLAUDE.md requires an `escalated` event after
N consecutive skips or silent failures. No `escalated` event was emitted. The pattern
also appeared earlier at 16:49Z and 18:48Z UTC on 2026-04-28 (flagged in
supervisor-reflection-2026-04-29T02-26-03Z §Observations #2).

The wrapper script (`scripts/lib/supervisor-tick.sh`) commits the tick branch and
emits a `session_reflected` event on failure, but has no consecutive-failure tracking
or S3-P2 escalation path. The obligation exists in the charter; the emission path
does not implement it.

## Impact

- Governance tick failures accumulate silently. Two consecutive failures (and likely
  more) passed undetected at the executive level.
- The S3-P2 rule's escalation trigger is dead code from the wrapper's perspective.
- An attended session reading only the event stream would see `session_reflected` events
  for failed ticks, not distinguishable from successes without reading the note field.

## Fix needed

The tick wrapper must track consecutive same-reason failure state (a counter file at
`runtime/.state/tick-consecutive-failures` or similar) and emit an `escalated` event
after N≥3 consecutive failures. The escalation should also write an URGENT handoff
to `supervisor/handoffs/INBOX/`.

## Evidence

- Events stream: `ts:2026-04-29T04:49:59Z note:"tick claude invocation failed"` and
  `ts:2026-04-29T06:49:58Z note:"tick claude invocation failed"` — no `escalated`
  between them.
- Cross-cutting synthesis 2026-04-29T03:24:29Z §Pattern 2 names this pattern.
- Supervisor-reflection-2026-04-29T02-26-03Z §Observations #2.
