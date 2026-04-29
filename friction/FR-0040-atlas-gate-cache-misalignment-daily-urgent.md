---
id: FR-0040
title: Atlas S3-P2 gate threshold misaligned with dataset cache — daily URGENT fires
status: Open
created: 2026-04-25T22:49Z
source: supervisor-tick-2026-04-25T22-49-35Z + atlas PM session handoff 2026-04-25T21-40Z
---

# FR-0040 — Atlas S3-P2 gate/cache misalignment creates daily URGENT cadence

## Observed friction

The atlas S3-P2 frozen-loop gate (`FROZEN_LOOP_ESCALATION_AFTER = 3 cycles`) fires approximately once per 24 hours during normal epistemic steady state, generating a daily URGENT escalation that requires attended executive intervention to dismiss.

## Root cause

Two constants are structurally misaligned:

- `FROZEN_LOOP_ESCALATION_AFTER = 3` (fires after 3 consecutive all-continue cycles, ~3 hours)
- `DATASET_RETEST_AFTER = 1 day` (prevents re-testing the same `(symbol, timeframe)` for 24 hours)

A productive cycle generates new evidence. The freshness cache then blocks any new evidence for ~23 hours. The gate fires after 3 of those stalled cycles. This is not a bug — the loop is genuinely stalled for 23 hours — but it produces noise that drowns real escalations in the queue.

## Evidence

- Atlas PM session handoff 2026-04-25T21-40Z: `cycle.escalated` event at 21:31Z, `evidence=153`, `streak_start_ts=1777145329577` (19:28Z). All-continue streak 6 cycles.
- Strategy readiness: research-only, 0 promoted primitives, 12 contradicts, 0 strong supports. The gate is working correctly; the underlying epistemic state is correct.

## Design options (per atlas PM session)

A — Accept the cadence; each URGENT is a valid daily "no new state" signal.  
B — Lengthen gate threshold to align with cache (e.g. 24 cycles). Reduces noise; loses early signal if loop dies entirely.  
C — Shorten `DATASET_RETEST_AFTER` (e.g. 6h). More cycles per day; more compute.  
D — Make gate cache-aware: skip emission while cache is blocking all hypotheses.

**This is a principal-class tuning decision.** Workspace S3-P2 rule pins threshold=3, so any change requires principal sign-off.

## Handoff

Principal decision pending. See `handoffs/ARCHIVE/2026-04/general-atlas-frozen-loop-diagnosis-2026-04-25T21-40Z.md` for full analysis. Active-issues updated with pending-principal entry.
