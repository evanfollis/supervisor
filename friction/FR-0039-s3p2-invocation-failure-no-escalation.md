# FR-0039: S3-P2 invocation failure gap — no escalated event

Captured: 2026-04-30T02:49Z
Source: reflection synthesis (2026-04-29T14:26Z, 2026-04-30T02:27Z); events stream
Status: open

## What happened

The supervisor tick invocation failed at three separate timestamps:
- 2026-04-29T04:49Z
- 2026-04-29T06:49Z
- 2026-04-30T00:49Z

Each failure produced a `session_reflected` event with a failure note in the event stream,
but no `escalated` event was emitted. The workspace charter (CLAUDE.md §S3-P2) is explicit:
"Any automated loop must emit a named `escalated` event after N consecutive skips or silent
failures. The threshold for the tick is 3 consecutive same-reason skips."

The charter rule has been live since ADR-0020. The first two failures (04:49Z, 06:49Z) were
consecutive — at that point an `escalated` event was already overdue.

## Why it matters

The escalation surface is the first line of defense against a stuck automation loop. A
supervisor tick that fails silently for 3+ windows is indistinguishable from a healthy one
unless the event stream specifically contains an `escalated` event. Without that, the
principal and reflection system have no positive signal that the loop is degraded.

The 00:49Z failure produced no `escalated` event despite the 3rd occurrence — the loop
degraded without triggering the designed alarm.

## Root cause / failure class

The tick wrapper (`scripts/lib/tick-wrapper.sh`) does not maintain consecutive-failure
state across invocations. Each invocation runs fresh; the wrapper has no memory of prior
failure counts. The S3-P2 rule cannot be satisfied without per-invocation-failure count
state persisted to disk between runs.

## Fix required (Tier-C — attended session)

Add consecutive-failure tracking to `tick-wrapper.sh`. The proposal and code sketch are
in INBOX: `proposal-tick-consecutive-failure-tracking-2026-04-29T15-29-09Z.md`.

Also a duplicate/companion proposal: `proposal-tick-postaction-verification-2026-04-29T03-28-39Z.md`
covers both this gap and the ghost-state pattern (FR-0038).

## Remaining work

- Land the consecutive-failure tracking code change (Tier-C, attended session required)
- After landing, verify the next invocation failure produces an `escalated` event
