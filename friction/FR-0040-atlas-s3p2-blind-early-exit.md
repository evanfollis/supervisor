---
name: FR-0040
slug: atlas-s3p2-blind-early-exit
status: Open
created: 2026-04-30
project: atlas
rule: S3-P2 (self-monitoring escalation after N consecutive stuck states)
---

# FR-0040: Atlas S3-P2 escalation blind to early-exit frozen state

## Observed friction

Atlas runner has been frozen for 14+ hours (since ~00:45Z 2026-04-30). Each cycle:
- `cycle.started` fires with "22 signals found"
- `generate_hypotheses()` returns empty because all signal→hypothesis hashes
  match `FALSIFIED` entries (signal-hash-drift: formulated hypotheses have
  parameter values from Apr 18–19; current signals generate different hashes)
- Runner early-exits without emitting `cycle.completed`
- `_maybe_escalate_frozen_loop` counts consecutive `cycle.completed` events
  with all-continue decisions — but `cycle.completed` is never emitted on the
  early-exit path
- Result: 15 `cycle.started` events, 1 `cycle.completed` (hypotheses_evaluated=0),
  0 `escalated` events across the freeze window

## Root cause

The S3-P2 escalation gate was designed for the happy-path terminal event
(`cycle.completed`). The early-exit path (no candidates generated) does not
emit `cycle.completed`, making the gate structurally incapable of detecting
this failure class. The runner appears operationally active (it starts cycles
and finds signals) but is effectively frozen.

This is an instance of the cross-cutting Pattern 1 from cross-cutting synthesis
2026-04-30T15:26Z: "Self-monitoring gates are blind to early-exit and
non-happy-path failures."

## Fix shape

Emit `cycle.completed` (or a distinct `cycle.skipped`) on EVERY exit path,
including the empty-candidates early exit. Include a `reason` field:
`no_candidates`, `invocation_failure`, `rate_limited`, etc. The S3-P2 gate
then operates on all exits, not only successful ones.

## Related

- cross-cutting synthesis 2026-04-30T15:26Z Pattern 1 and Pattern 2
- `runtime/.handoff/atlas-pool-rotation-synthesis-update-2026-04-30T16-48Z.md`
- FR-0039 (ghost-write pattern — same failure class, supervisor project)
