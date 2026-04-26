---
name: FR-0040 — atlas frozen-loop gate firing on cached/stale scoring data
description: Atlas daily gate is firing as expected but may be evaluating stale scoring data, making designed throttling indistinguishable from stuck behavior
status: Open — pending principal decision on acceptable staleness window
created: 2026-04-25T22:49Z
discovered-by: supervisor-tick-2026-04-25T22-49-35Z
related-handoff: runtime/.handoff/general-atlas-frozen-loop-diagnosis-2026-04-25T21-40Z.md (archived)
---

# FR-0040 — Atlas gate/cache misalignment

## Status: Open

## Observed behavior

The atlas frozen-loop gate fires correctly on a daily cadence. However, a handoff from the atlas session (2026-04-25T21:40Z) reports the gate evaluates candidates against data that may be stale or cached from a prior scoring run. This makes it hard to tell whether the daily throttle is correctly rejecting candidates (designed behavior) or stuck on a stale evaluation.

## Principal-class tuning decision needed

The principal needs to decide the acceptable staleness window before implementation can proceed. Listed in `active-issues.md` under Pending principal.

## Fix direction

1. Align scoring timer cadence with gate evaluation window so the gate always runs against fresh data.
2. Add telemetry payload including the age of underlying scoring data when the gate fires.
3. Gate should emit `throttled` (not `failure`) and log staleness explicitly when scoring data age exceeds the threshold.
