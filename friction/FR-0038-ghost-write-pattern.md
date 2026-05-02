---
id: FR-0038
title: Ghost-write pattern — tick sessions claim file writes that don't land
status: Open
created: 2026-04-28
updated: 2026-05-02
source: multiple tick sessions (04-26 through 05-02)
---

# FR-0038: Ghost-write pattern

## What happened

Multiple consecutive supervisor tick sessions emitted events claiming successful
file writes (FR records, active-issues.md updates) that did not land on main.
The writes were executing against tick branches that were never merged, so from
main's perspective the files were never written. Sessions had no indication their
writes were going to a branch rather than main — no error, no warning.

This persisted across at least 9 tick windows (2026-04-26 through 2026-05-02).

## Why it matters

Carry-forward escalation gates check for unresolved observations. A ghost-write
that emits a "verified" event closes the gate without the underlying work
actually landing. The result: the escalation surface produces false confidence,
and recurring structural problems accumulate silently.

## Contributing factors

1. Tick sessions run on branches (`ticks/YYYY-MM-DD-HH`), not on main
2. `reflect.sh` (and the tick wrapper) don't `git checkout main` before the session
3. The session has no way to know whether its writes will be merged
4. The verification step ("ls friction/ confirms FR-0038 exists") runs inside the
   same branch where the write just happened — it looks correct in-branch

## Fix direction

The tick wrapper should either:
- Run the session after `git checkout main` (simplest)
- Or gate verification against main's state (cross-branch ls won't work)

Until fixed: tick sessions must not emit "verified on disk" claims for file writes.
State a write is pending merge, not that it succeeded permanently.

## Status notes

FR-0038 through FR-0042 were ghost-claimed in multiple tick event logs. This file
is the first actual landing (2026-05-02 attended session).
