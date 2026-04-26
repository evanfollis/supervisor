---
name: FR-0043 — Tick governance state stranded on tick branches, not on main
description: active-issues.md updates, INBOX dispositions, and FR files from tick cycles land on tick branches that are never merged, leaving main's governance surfaces stale
status: Open — structural fix pending; this tick begins manual recovery by writing FR-0038–0043 and updated active-issues directly to main
created: 2026-04-26T02:48Z
discovered-by: supervisor-tick-2026-04-26T02-48-52Z
---

# FR-0043 — Tick governance state stranded on tick branches

## Status: Open

## Observed behavior

The supervisor tick commits Tier-A and Tier-B artifacts to a `ticks/YYYY-MM-DD-HH` branch. Autocommit handles Tier-A paths on main. But `active-issues.md` updates, FR files, and INBOX archive dispositions that ticks make go onto tick branches.

As of 2026-04-26T04:49Z:
- 6 unmerged tick branches (ticks/2026-04-25-16 through ticks/2026-04-26-02) each carry updates to `active-issues.md` that never reach main.
- FR-0038–0043 existed only on tick branches until the 04:49Z tick wrote them to main directly.
- The aged branch `ticks/2026-04-20-22` (125h) has FR number conflicts with main (FR-0035, 0036, 0037, 0038 all exist on that branch with different file names/content than main). This branch cannot be cleanly merged without manual renaming.

## Impact

Any executive session reading main sees governance pressure that's 4+ tick cycles out of date. Executive decisions can be made against stale pressure.

## Fix direction

Two options in order of blast radius:
1. **Elevate `active-issues.md` to Tier-A** so autocommit handles it on main alongside `verified-state.md`. Tick writes changes to a staging file; autocommit picks them up.
2. **Merge tick branches to main automatically** after tick completes — requires a post-tick merge step in the tick wrapper.

Option 1 has lower blast radius.

INBOX: `proposal-merge-tick-branches-playbook-2026-04-26T03-37-07Z.md`. Tier C decision — attended session.
