---
id: FR-0041
title: Tick branch governance updates strand from main
status: Open
created: 2026-04-26T02:48Z
detected-by: supervisor-tick-2026-04-26T02-48-52Z
---

# FR-0041 — Tick branch governance stranding

## Observation

Seven tick branches exist as of 2026-04-26T06:49Z (`ticks/2026-04-20-22` at 127h+; 6 from the last 34h). Each contains active-issues updates, FR files, and pressure items. Main branch has none of this. Any executive session reading main sees governance state that is 4-6h stale at best, 127h+ stale at worst. The remote push gap compounds this: 33 commits ahead of `origin/main`.

## Impact

Governance is fictional relative to what remote or next-session readers see. Reflections, synthesis, and downstream agents reading main-branch state are working from materially stale data. The entire reflection/synthesis loop depends on current-state files being accurate — stranded branches break this assumption.

## Root cause hypothesis

The tick script creates a named branch, commits, pushes to that branch, then exits. Merging tick branches to main requires attended session action or a merge automation that doesn't exist. The 127h branch (`ticks/2026-04-20-22`) has merge conflicts per doctor output — it can't be auto-merged.

## Proposed fix class

- Automate merging of conflict-free tick branches to main in the tick script itself (after push, attempt `git merge --ff-only`; if clean, push main; if not, leave the URGENT doctor warning).
- Alternatively: restructure ticks to commit directly to main rather than a named branch (significant workflow change, but eliminates the problem class).
- Minimum: attended session must merge or delete aged tick branches within the 72h SLA.
