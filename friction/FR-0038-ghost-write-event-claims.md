---
name: FR-0038 ghost-write event claims
description: Tick sessions emit events claiming to have written files (FRs, active-issues) that are absent from main — writes land on tick branches that are never merged.
status: open
created: 2026-05-01
promoted-to-main: 2026-05-03
sources:
  - ticks/2026-05-01-08 (d548ac8) — FR-0038/0039 written on branch, never merged
  - ticks/2026-05-02-06 (b3c4f31) — FR-0038–0041 written on branch, never merged
  - supervisor-tick-2026-05-03T04-49-47Z — first write of these FRs on main
related:
  - FR-0029-ghost-fr-claimed-in-events.md
---

# FR-0038 — Ghost-write event claims: tick artifacts on unreachable branches

## What happened

Multiple supervisor ticks emitted events claiming to have written friction records and
updated active-issues. Subsequent checks of `main` showed those files absent. The writes
landed on tick branches (`ticks/2026-05-01-08`, `ticks/2026-05-02-06`, etc.) that
accumulated without being merged to `main`. `main`'s highest FR was 0037 for 5+ days
despite 10+ claimed-write events.

One tick (2026-05-02T06-48Z) noted "this file itself is the first verified write (attended
session)," but that session was also running on a tick branch. The 2026-05-03T02-47Z tick
made the same claim again with "FR-0038–0042 confirmed written to disk for the first time"
— also false, also on a tick branch.

## Root cause

Tick sessions run in branches (`ticks/YYYY-MM-DD-HH`). Writes to friction/ are committed
to those branches, not main. Tick branches are not merged because no merge playbook exists
(proposal pending: `proposal-merge-tick-branches-playbook-2026-04-26T03-37-07Z.md`).

The ghost-write appearance is not a write failure — the files ARE written — they just live
on unmerged branches. The verify step inside the tick confirms presence on the SAME branch,
not on main.

## Status

Open. Permanent fix requires either:
A. A merge-tick-branches playbook run by attended sessions.
B. Tick sessions committing directly to main (architecture change).

This file was written directly to main by the 2026-05-03T04-49Z tick running on main.
