---
id: FR-0038
title: Ghost FR materialization — tick sessions emit fr_captured events for files that never land on main
status: Open
created: 2026-04-28
source: supervisor-ticks + reflection-2026-04-28T14-24-02Z
---

# FR-0038: Ghost FR materialization

## What happened

5+ consecutive tick sessions (Apr 26–28) each emitted `fr_captured` events claiming
FR-0038 and FR-0039 were written to `friction/`. Neither file existed on `main`
until manually written in the 20:47Z Apr 28 tick (direct session, not worktree).

The `fr_captured` events in `supervisor-events.jsonl` were structurally accurate —
the tick did write the files — but the files landed in unmerged tick branches, not
main. Downstream sessions reading events to determine "what exists" got false signal.

## Root cause

Tick sessions run on tick branches (e.g. `ticks/2026-04-28-XX`). Writes to
`friction/` succeed within the tick's branch but are never merged to main.
The event emission happens before the branch divergence is visible, so events
claim materialization on `main` when the file is only on `ticks/*`.

## Failure class

A materialization event without a "landed on main" gate conflates "written to
branch" with "exists in the authoritative state". Any consumer of `fr_captured`
events that doesn't also check `git show main:friction/<file>` will get ghost data.

## Fix path

Option A: Tick sessions should only emit `fr_captured` after verifying
`git show main:friction/<file>` — but ticks can't write to main directly.

Option B: The autocommit loop should merge tick branches to main after each cycle,
making branch writes = main writes. This is the `proposal-merge-tick-branches-playbook`
in INBOX.

Option C: Attended session periodically merges aged tick branches (manual, labor-intensive).

Preferred: Option B.

## Status

Open. FR-0038 and FR-0039 are now materialized on main via direct session write
(2026-04-28T20-47Z). The structural cause remains unfixed.
