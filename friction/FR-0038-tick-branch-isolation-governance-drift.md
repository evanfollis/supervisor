---
id: FR-0038
title: Tick-branch isolation causes governance surfaces to drift from main
status: Open
severity: high
first_observed: 2026-05-01
recorded: 2026-05-04
---

# FR-0038: Tick-branch isolation causes governance surfaces to drift from main

## What happened

Tick sessions (the 2h automated supervisor cadence) commit Tier-A changes
to named tick branches (`ticks/YYYY-MM-DD-HH`) rather than directly to
main. The branches are pushed but never merged. This means every Tier-A
write by a tick — updates to `system/active-issues.md`, new FR files,
`system/verified-state.md` regeneration, event appends — accumulates on
tick branches and does not affect the production state on main.

Observed effects:
- `system/active-issues.md` frontmatter showed `updated: 2026-04-25` on
  main while ~10 tick branches contained updates written on 2026-05-01 through
  2026-05-03. The main-branch version was 8+ days stale despite 20+ ticks
  attempting to update it.
- FR-0038 through FR-0044 were written to tick branches in prior cycles
  but never appeared on main. The highest FR on main remained FR-0037
  across 14+ ticks.
- `system/verified-state.md` regenerated every tick but the regeneration
  only persists on tick branches.
- Events appended to `events/supervisor-events.jsonl` on tick branches do
  accumulate on main because the autocommit cron picks them up separately.

## Root cause

The tick wrapper script (`scripts/lib/supervisor-tick.sh`) creates the
tick branch before running the Claude session, then commits any working-
tree changes to that branch. Attended merge of tick branches to main
is required but has no automated mechanism.

## Impact

- Governance surfaces on main are perpetually stale; attended sessions
  work from stale context.
- FR backlog on main understates reality by 7+ records.
- active-issues.md does not reflect live issues written by ticks (atlas
  runner frozen, reflect.sh Write bypass) until an attended session merges
  or manually edits.
- The "active-issues updated on main" claim in tick events is misleading —
  changes land on a tick branch named for that tick, not on the branch
  named `main`.

## Fix path

Option A (structural): Add a merge step to the tick wrapper that merges
the tick branch to main after commit (or commits directly to main for
Tier-A surfaces and only branches for Tier-B drafts).

Option B (attended): Run a periodic attended merge of tick branches to
main. Playbook needed.

Option C (work-around): For the specific Tier-A surfaces that decay fastest
(active-issues.md, verified-state.md), have the tick commit directly to
main rather than the tick branch. Tier-B drafts still go to tick branches.

Fix lives in `scripts/lib/supervisor-tick.sh` (Tier-C — requires attended
operator session).
