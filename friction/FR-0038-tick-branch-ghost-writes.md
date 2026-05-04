---
id: FR-0038
title: Tick sessions write to tick branches; events claim main-branch writes that never land
created: 2026-05-04
status: open
severity: high
pattern: structural
---

# FR-0038: Tick-branch ghost-writes

## What happens

Tick sessions run on `ticks/YYYY-MM-DD-HH` branches. When they write
Tier-A files (friction records, INBOX handoffs, active-issues updates)
and emit events claiming those writes "landed on main," the files are
actually on the tick branch. Main only receives the autocommit job's
cherry-pick of tick-branch Tier-A paths — but only what was actually
committed in the tick session's branch commit. If the tick event log
says "FR-0038 written to main" but the autocommit job runs before main
receives the cherry-pick, or if cherry-pick path filtering misses the
file, the claim is false.

## Observed instances

- 2026-05-04T00:49Z tick: emitted `session_reflected` claiming "FR-0038
  written to main (tick-branch isolation root cause)." As of the 02:49Z
  tick, `friction/FR-0038-*.md` does not exist on main. The event log
  contains a false state claim.
- Multiple previous ticks: `active-issues updated` events on tick
  branches while main's active-issues.md remained at 2026-04-25 date.
- Reflection at 2026-05-04T02:26Z explicitly flags: "ghost-write false
  state claims in event log" as a critical observation.

## Why it matters

The supervisor's truth hierarchy lists "events stream" as a high-confidence
source. Events claiming writes that didn't land silently corrupt the
control plane's state model. Subsequent ticks read stale state and believe
it is current. The carry-forward escalation rule misfires — an observation
appears "resolved" (event says fix committed) but the fix is not live.

## Root cause

Tick sessions execute in their own git branch context. They write files
to disk and the wrapper script stages + commits to the tick branch. The
autocommit job (`workspace-autocommit.timer`) then reads Tier-A path
patterns from the tick branch and stages them on main. But the tick
session's event log is written before the autocommit job runs — the
tick can only claim what it staged to its own branch, not what eventually
lands on main.

## Fix direction

1. **Short term**: Tick sessions should not emit "written to main" in
   event notes. They should say "written to tick branch — pending
   autocommit." The autocommit job (or its hook) should emit the
   "landed on main" event.
2. **Medium term**: The autocommit job should emit a `tier_a_committed`
   event after successfully merging tick-branch Tier-A content to main,
   referencing the list of files merged.
3. **Structural**: Tick sessions that can write directly to main (e.g.
   when running in an attended session rooted at /opt/workspace/supervisor
   on main) should do so and skip the branch dance.

Fix is in `scripts/lib/supervisor-tick.sh` and the autocommit job
(Tier-C; requires operator-capable attended session).
