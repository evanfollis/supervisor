---
name: FR-0043 — Tick governance state stranded on tick branches, not on main
description: active-issues.md updates, INBOX dispositions, and pressure items from tick cycles land on tick branches that are never merged, leaving main's governance surfaces 4+ cycles stale
status: Open
created: 2026-04-26T02:48Z
discovered-by: supervisor-tick-2026-04-26T02-48-52Z
---

# FR-0043 — Tick governance state stranded on tick branches

## Status: Open

## Observed behavior

The supervisor tick commits Tier-A and Tier-B artifacts to a `ticks/YYYY-MM-DD-HH` branch. The autocommit mechanism commits Tier-A paths (session summaries, verified-state) directly to main. But active-issues.md updates, INBOX archive dispositions, and pressure-queue changes that ticks make go onto tick branches.

As of 2026-04-26T02:48Z:
- `active-issues.md` on main is `updated: 2026-04-25` and does not reflect the atlas gate tuning item added by the 22:49Z tick (confirmed by supervisor-reflection-2026-04-26T02:27Z).
- The tick branch `ticks/2026-04-25-22` has this update; main does not.
- A session reading main sees the wrong pressure state.

## Impact

Any executive session, reflection job, or attended session that reads `main` sees stale governance pressure. This means executive decisions can be made against pressure that's 4+ tick cycles out of date. The tick loop is doing governance work that never propagates to the canonical governance surface.

## Fix direction

Two options:
1. **Merge tick branches to main automatically after the tick completes** — requires a merge/push in the tick wrapper, which the wrapper currently blocks to prevent push during tick. Needs a designated post-tick merge step.
2. **Change Tier-A designation for active-issues.md** — make `active-issues.md` a true Tier-A path so the autocommit mechanism handles it separately, like `verified-state.md`. The tick writes its active-issues changes to a staging file; autocommit picks them up and commits to main.

Option 2 has lower blast radius. The autocommit path is already working for other Tier-A surfaces.

Tier C decision — requires attended session to approve architecture change and update tick/autocommit scaffolding.
