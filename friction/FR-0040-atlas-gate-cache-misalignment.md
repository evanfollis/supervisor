---
name: FR-0040 — atlas frozen-loop gate firing on cached/stale scoring data
description: Atlas daily gate is firing as expected but the gate's candidate evaluation is operating on data that may be cached or lagged, making it difficult to distinguish designed throttling from stuck behavior
status: Open
created: 2026-04-25T22:49Z
discovered-by: supervisor-tick-2026-04-25T22-49-35Z
related-handoff: runtime/.handoff/general-atlas-frozen-loop-diagnosis-2026-04-25T21-40Z.md
---

# FR-0040 — Atlas gate/cache misalignment

## Status: Open

## Observed behavior

The atlas frozen-loop gate fires correctly on a daily cadence. However, a handoff from the atlas session (2026-04-25T21:40Z, archived to INBOX) reports that the gate's evaluation of candidate quality is operating against data that may be stale or cached from a prior scoring run. This makes it hard to tell whether the daily throttle is correctly rejecting candidates (designed behavior) or is stuck on a stale evaluation (misalignment).

## Principal-class tuning decision needed

The principal needs to decide whether to tune the gate's cache invalidation window or the scoring cadence so the gate reliably evaluates fresh data. This is a commercial signal quality question, not a pure engineering question.

## Fix direction

1. Align scoring timer cadence with gate evaluation window so the gate always runs against a freshly-scored candidate set.
2. Add a telemetry event when the gate fires and include the age of the underlying scoring data in the event payload.
3. If scoring data age exceeds a threshold, gate should emit `throttled` (not `failure`) and log the staleness explicitly.

Pending principal decision on acceptable staleness window before implementation.
