---
id: FR-0038
title: Ghost FR materialization — events claim fr_captured but files never written
status: Open
created: 2026-04-28T10:47Z
source: supervisor-tick-2026-04-28T10-47-45Z
---

# FR-0038: Ghost FR materialization

## Observed behavior

`events/supervisor-events.jsonl` shows `fr_captured` events for FR-0038 and FR-0039 from
four separate ticks (2026-04-27T20Z, 2026-04-28T02Z, 2026-04-28T04Z, 2026-04-28T08Z), each
claiming to "materialize" these FRs. The actual files were never written to disk. Each tick
started fresh, saw no FR-0038/0039 files, "created" them, emitted events, and committed
(or tried to commit) — but the files never persisted.

## Evidence

```
grep fr_captured events/supervisor-events.jsonl
# → fr_captured for FR-0038 at 2026-04-28T02:49Z, 2026-04-28T04:50Z, 2026-04-28T08:50Z
# → fr_captured for FR-0039 at 2026-04-28T04:50Z, 2026-04-28T08:50Z
ls friction/FR-003{8,9}*  → "not found"
```

## Root cause hypothesis

Tick sessions that wrote these FRs were operating on tick branches (not main). The commits
went to the tick branch. main never received the merge. So from any session reading the main
branch working tree, the files don't exist. The same sessions then see no files, re-create,
re-commit on a new tick branch — producing the ghost loop.

This is a symptom of the broader tick branch stranding problem: >22 tick branches with
governance commits that were never merged to main.

## Fix

1. Merge the tick branches to main (resolve the tick branch stranding — see FR below)
2. After merge, verify FR-0038/0039 files appear on main
3. Long-term: ensure ticks commit to main, not to separate branches that go unmerged

## Status

Open. First real materialization: 2026-04-28T10:47Z (this tick, running on main).
