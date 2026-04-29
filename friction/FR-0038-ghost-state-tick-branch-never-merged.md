---
id: FR-0038
title: Tick sessions write Tier-A changes to tick branches that are never merged to main
status: Open
created: 2026-04-29
reported-by: supervisor-tick-2026-04-29T22-49-57Z
---

# FR-0038: Ghost-state — tick branch changes never merged to main

## What happened

Tick sessions from 2026-04-29T12:49Z onward claimed in events to have
written FR-0038 ("ghost-state pattern") to `main`. All event notes read:
"FR-0038 written on main." The filesystem as of 2026-04-29T22:49Z shows
only FR-0037 — FR-0038 does not exist on main.

Similarly, multiple ticks reported "active-issues updated on main" with
atlas pool rotation and INBOX saturation entries. Those entries do not
appear in `main:system/active-issues.md` as of this tick.

## Root cause

Tick sessions run on `ticks/YYYY-MM-DD-HH` branches. When they write
Tier-A files (friction, active-issues, events), those writes land on the
tick branch — not on main. The tick wrapper commits the branch and pushes
it (`ticks/YYYY-MM-DD-HH`), but the branch is never merged to main. The
events system records the write with "on main" framing, but main never
receives the commit.

The result: every subsequent tick session reads events claiming the
action completed, trusts that state, and skips the write. The action
never lands. The event log becomes a false record.

## Why it's a ghost-state failure

The pattern is self-reinforcing: the more ticks report an action complete,
the less likely any future tick is to re-examine whether main actually
contains the change. Only an attended session, or a tick explicitly running
`git checkout main` before writing, can break the cycle.

This is a structural variant of FR-0029 (ghost-FR-claimed-in-events), but
broader: any Tier-A write from a tick branch suffers this risk unless the
tick explicitly lands the commit on main before pushing.

## Impact

- FR records: FR-0038 has been "written" in events 3+ times but was absent
  from main until this filing.
- Active-issues: atlas pool rotation and INBOX saturation entries that
  ticks claimed to add to active-issues were not on main.
- Verified-state: the `updated:` field in active-issues remained 2026-04-25
  despite multiple tick claims of updates.
- The synthesis meta-loop operates on main-branch state; tick-branch-only
  changes are invisible to it.

## Fix direction

The tick wrapper script (`supervisor-tick.sh` or equivalent) should:
1. Checkout `main` before writing Tier-A governance files.
2. Commit Tier-A changes directly to `main` (not to the tick branch).
3. Push `main` separately from the tick branch.

Or: Tier-A files should be written before the tick branch is created,
directly on main, so no merge step is needed.

This is a Tier-C scripts/lib change and requires an attended session.

## Status

Open. Requires attended-session fix to `scripts/lib/supervisor-tick.sh`
or equivalent wrapper. Until fixed, tick sessions writing Tier-A changes
SHOULD explicitly checkout main, write, and commit before creating the
tick branch.
