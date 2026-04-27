---
id: FR-0038
title: Tick events falsely claim commits landed on main when they land on tick branches
severity: CRITICAL
created: 2026-04-27T02-49Z
status: open
source: supervisor-tick-2026-04-27T02-49-05Z
---

# FR-0038 — Tick event labels claim "main" for tick-branch commits

## Observation

Supervisor tick sessions emit `session_reflected` events with notes like
"materialized on main" or "promoted to main" for FR files and other Tier-A
artifacts. These commits actually land on the current tick branch
(e.g. `ticks/2026-04-26-18`), not on `main`. The event record actively lies
about artifact location.

## Evidence

- FR-0038 through FR-0043 were all claimed in events.jsonl as "on main" across
  multiple tick sessions (04-26T18, 20, 22). None exist in `friction/` on main.
- `git ls-tree` across tick branches shows divergent FR files with conflicting
  content under the same ID (FR-0038 through FR-0043 have different filenames
  and bodies across `ticks/2026-04-26-{18,20,22}`).
- This is the 12th+ instance of the ghost-FR pattern (FR-0029 filed 2026-04-22).

## Root cause

`supervisor-tick.sh` event-emission code hard-codes "main" as a convenience
label in the `session_reflected` note string. It never reads the actual current
branch at commit time. The static string propagates into events.jsonl, making
downstream consumers (reflections, synthesis, executive) believe Tier-A changes
are on main when they are not.

## Impact

- Ghost FRs: valid friction observations filed on tick branches, never visible
  on main, never acted on.
- Tick branch stranding: branches age past 72h SLA because they contain
  governance artifacts (not just reports) that require attended merge judgment.
- Remote push gap: governance state grows on branches; main falls behind.
- Meta-loop integrity: synthesis and reflection read main; they diagnose
  "not fixed" for issues that appear fixed only on branches.

## Required fix (Tier-C — attended session)

In `supervisor-tick.sh`, at the commit step, capture the actual branch:

```bash
ACTUAL_BRANCH=$(git -C "$REPO" branch --show-current)
```

Use `$ACTUAL_BRANCH` in the event note rather than the static "main" string.
This is synthesis Proposal 1 [CRITICAL] from 2026-04-26T15:25Z.
