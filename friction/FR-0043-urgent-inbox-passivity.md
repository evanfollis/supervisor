---
id: FR-0043
title: URGENT INBOX items accumulate without attended session pickup
status: Open
created: 2026-04-26T02:48Z
detected-by: supervisor-tick-2026-04-26T06-49-45Z
---

# FR-0043 — URGENT INBOX passivity

## Observation

`URGENT-adr-review-gap-0031-0032-routed-2026-04-25T16-47Z.md` and `URGENT-doctor-tick-branch-aged-2026-04-25T16-47Z.md` have been in INBOX since 2026-04-25T16:47Z. Seven consecutive tick runs have deferred them citing "requires attended session." No attended session has acted on them in 14h+.

The tick's carry-forward escalation rule (3 consecutive same-reason defers → write a second URGENT) was described in the charter but is not implemented mechanically. Ticks note the items and move on.

## Impact

URGENT designation is losing meaning. Items that require the principal's attention are not surfacing effectively if ticks just defer them indefinitely. The escalation surface degrades into background noise.

## Root cause hypothesis

The charter says "carry-forward escalation: 3 consecutive same-reason skips → write URGENT" but no tick checks the defer count. Each tick rediscovers the deferral independently and writes the same note without escalating the urgency signal.

## Proposed fix class

- Tick should maintain a defer-count for each INBOX item (e.g., add a `defer_count` header to the handoff file itself, or track via a small state file).
- After 3 defers, write a new `URGENT-escalated-<original-slug>-<iso>.md` in INBOX and note that the original has been deferred N times.
- Alternatively: attended session must be more reliably present — the structural gap is that the attended session window is too narrow relative to the INBOX accumulation rate.
