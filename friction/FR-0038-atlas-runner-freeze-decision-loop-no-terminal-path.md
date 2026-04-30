---
id: FR-0038
title: Atlas runner freeze — decision loop has no terminal path when principal doesn't respond
status: Open
created: 2026-04-30T18:48Z
source: supervisor-tick-2026-04-30T18-48-33Z
project: atlas
pattern: escalation-loop-without-terminal-disposition
---

# FR-0038: Atlas runner freeze — decision loop has no terminal path

## What happened

Atlas runner has been frozen since ~00:45Z 2026-04-30 (~18h). The root cause
has two independent blockers:

1. **BitMEX/Kraken Futures data unavailability** — 2 `testing` hypotheses
   require data not available from Hetzner US; they perpetually decide `continue`.

2. **Signal-hash drift** — 12 `formulated` hypotheses were created Apr 18–19
   with parameter values from that date. Current signal scans find the same
   patterns but with different values → different claim hashes → the formulated
   pool is structurally unreachable.

The first pool-rotation decision handoff was written 2026-04-29T17:00Z. A 24h
deadline was set. The deadline elapsed at 2026-04-30T17:00Z without a principal
response. A v2 handoff was written at 17:00Z with updated decision matrix
incorporating the newly discovered signal-hash-drift blocker.

## The failure class

The escalation path (URGENT INBOX) exists and fired correctly. But the path
has no terminal disposition if the principal doesn't respond within the
deadline window. The system re-escalates the same issue without a fallback:
no auto-expiry, no degraded-mode behavior, no safe default that keeps the
runner functional.

Result: runner stays frozen indefinitely. Each tick correctly identifies the
freeze but cannot act without principal direction. 26+ hours lost.

## Why this recurred

- No "safe default" behavior defined for the runner when the decision loop
  stalls (e.g., "kill infeasible hypotheses after N days without principal
  response; continue with remaining pool").
- The original handoff options (A/B/C) were written before the signal-hash-drift
  blocker was identified, so the v2 had to supersede — adding another cycle.
- S3-P2 monitoring was blind to the early-exit path for 14+ hours before the
  04-30T14:29Z fix landed in `9708867`.

## Recommended structural fix

Define a "runner self-recovery" policy in the atlas CLAUDE.md or runner config:
- After N consecutive all-continue or all-skip cycles (e.g., 10), runner may
  auto-advance formulated → testing using the oldest available + feasible hypothesis.
- After M consecutive cycles with 0 testable hypotheses, runner emits
  `runner.stuck` escalation AND auto-suspends (rather than looping indefinitely).
- Hypotheses with unavailable data sources are auto-marked `INFEASIBLE` after
  K consecutive data-fetch failures (removes the manual deprecation step).

The decision loop is the right escalation path for novel architectural changes.
It is the wrong path for routine operational recovery.
