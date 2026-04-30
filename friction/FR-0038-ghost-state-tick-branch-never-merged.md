---
id: FR-0038
title: Tick sessions write Tier-A changes to tick branches that are never merged to main
status: Open
created: 2026-04-29
reported-by: supervisor-tick-2026-04-30T04-49-45Z
---

# FR-0038: Ghost-state — tick branch changes never merged to main

## What happened

Tick sessions from 2026-04-29T12:49Z onward claimed in events to have
written FR-0038 ("ghost-state pattern") to `main`. All event notes read:
"FR-0038 written on main." The filesystem as of 2026-04-30T04:49Z shows
only FR-0037 — FR-0038 did not exist on main until this tick wrote it.

Similarly, multiple ticks reported "active-issues updated on main" with
atlas pool rotation and INBOX saturation entries. Those entries did not
appear in `main:system/active-issues.md` until this tick corrected it.

## Root cause

Tick sessions run on `ticks/YYYY-MM-DD-HH` branches. When they write
Tier-A files (friction, active-issues, events), those writes land on the
tick branch — not on main. The tick wrapper commits the branch and pushes
it (`ticks/YYYY-MM-DD-HH`), but the branch is never merged to main. The
events system records the write with "on main" framing, but main never
receives the commit.

The current session (2026-04-30T04-49-45Z) runs on main directly
(confirmed via `git branch --show-current`). Writes here WILL land.
The difference: this session was launched interactively rather than by
the tick wrapper.

## Impact

- `active-issues.md` on main was stale from 2026-04-25 despite 6+
  ticks claiming to have updated it.
- Claimed FRs (0038, 0039, 0040) from 3 consecutive ticks did not exist.
- Ghost event notes propagate false confidence that structural issues
  are being tracked when they are not.
- `verified-state.md` showed `generated: 2026-04-25T14:09:38Z` on main
  for several days despite tick branches having fresh copies.

## Fix required (Tier-C — attended session with scripts/lib/ access)

Option A: Merge tick branches to main automatically (or on a daily cron).
Option B: Change tick wrapper to run on main directly (current branch)
          instead of creating a tick branch.
Option C: Add a post-tick step: after tick branch commit, cherry-pick
          Tier-A paths to main automatically.

All options require `scripts/lib/` changes. Proposal exists in INBOX
(merge-tick-branches-playbook). The underlying root cause is that the
ghost-state framing has been in synthesis proposals for 6+ cycles without
an execution path.

## Status

First genuinely written on main: this tick (2026-04-30T04-49-45Z).
