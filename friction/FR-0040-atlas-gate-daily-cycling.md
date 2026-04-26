---
id: FR-0040
title: Atlas S3-P2 gate fires correctly but hypothesis pool not advancing
status: Open
created: 2026-04-25T22:49Z
detected-by: supervisor-tick-2026-04-25T22-49-35Z
---

# FR-0040 — Atlas S3-P2 gate fires daily; hypothesis pool frozen

## Observation

The atlas S3-P2 escalation gate correctly detects 3 consecutive all-continue cycles and writes/deletes an URGENT. However, the gate fires daily because `DATASET_RETEST_AFTER=1day` causes the cache to refresh, experiments to rerun, and the same 5 hypotheses to produce the same "continue" decision again. Evidence frozen at 153 entries. 19 formulated hypotheses have never been evaluated — the runner always fills evaluation slots from the signal scanner, not the existing pool.

## Impact

The gate is working as designed but is permanently triggered — signal-to-noise ratio degrading. The hypothesis pool is not actually advancing. The escalation surfaces to the principal on a daily cadence but the same situation exists each time.

## Root cause hypothesis

Two distinct issues compounded:
1. `DATASET_RETEST_AFTER=1day` is shorter than the innovation cycle needed to actually change hypothesis outcomes.
2. The signal scanner preferentially generates new hypotheses over pulling from the formulated pool — evaluation coverage is biased toward fresh over depth.

## Principal-class decision required

- Extend `DATASET_RETEST_AFTER` to a longer window to reduce churning.
- Or: modify runner to pull from the formulated pool (19 items) before generating new ones.
- Or: review whether the 5 evaluated hypotheses represent the right direction at all.

This is tracked as a principal-class decision pending in active-issues.
