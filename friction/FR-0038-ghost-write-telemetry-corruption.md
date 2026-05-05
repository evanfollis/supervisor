---
id: FR-0038
title: Ghost-write telemetry corruption — events claim FR files written; files never land on main
status: Open
created: 2026-05-05
source: supervisor-tick pattern (8+ cycles)
---

# FR-0038: Ghost-write telemetry corruption

## What happened

Events in `supervisor-events.jsonl` have claimed `friction_captured` events for FR-0038 and FR-0039 on 8+ separate tick cycles (2026-05-04 through 2026-05-05T02:47Z). Each event body says "written on main for real." The files were never present in `friction/` on `main`.

Parallel pattern: `reflect-sh-disallow-list-gap-2026-05-01T16-48Z.md` in INBOX references `friction/FR-0040-reflect-sh-disallow-list-gap.md` which also does not exist.

## Root cause

Tick sessions run on per-tick branches (e.g. `ticks/2026-05-04-22`). When a tick emits `friction_captured` and claims the file is on `main`, it is wrong — the file exists only on the tick branch. The tick's branch is supposed to be merged to `main` by the wrapper, but:
1. The wrapper merge has been failing silently, or
2. The tick emits the event before the merge and doesn't re-check after.

The result: ghost events accumulate, the telemetry log appears to show friction being captured, but the friction surface on `main` has no new records.

## Impact

- Friction surface understates recurring patterns — the event log is not reliable evidence of what's been captured.
- `workspace.sh doctor` fires the "friction stale >7 days" warning but the cause is not obvious from the warning text alone.
- S3-P2 self-monitoring rule depends on friction records being present; ghost events defeat it.

## Fix

1. After writing a Tier A file, verify it exists on the current branch AND on `main` (or that the branch has been merged) before emitting `friction_captured`.
2. Alternatively: emit events only after the merge step confirms success.
3. The wrapper script (`supervisor-tick.sh`) should fail-loudly if the merge step fails rather than proceeding to push with a clean-looking event log.

## Status

Open — fix requires attended session (scripts/lib/ is Tier C).
