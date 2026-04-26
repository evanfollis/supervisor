---
id: FR-0044
title: Reflection dirty-tree guard fires on expected ARCHIVE writes
status: Open
created: 2026-04-26T08:48Z
detected-by: supervisor-tick-2026-04-26T08-48-21Z
---

# FR-0044 — Reflection dirty-tree false positive on ARCHIVE writes

## Observation

`runtime/.handoff/URGENT-supervisor-reflection-dirty-tree.md` was written by the 2026-04-26T02:27Z supervisor reflection session. Content:

> After: `?? handoffs/ARCHIVE/2026-04-26/session-summary-supervisor-2026-04-26T02-31-10Z.md`

The guard treated writing a session-summary to `handoffs/ARCHIVE/` as an unexpected dirty-tree mutation. But archiving session summaries during reentry is explicit expected behavior per the charter (§Reentry hygiene: "workspace.sh context auto-archives session-summary-* files in supervisor/handoffs/INBOX/ on every reentry").

## Impact

False-positive URGENTs degrade trust in the dirty-tree guard and create noise for the general session. The URGENT-supervisor-reflection-dirty-tree.md file at `runtime/.handoff/` requires manual review and cleanup.

## Root cause hypothesis

The dirty-tree guard compares `git status --porcelain` before and after the reflection session. It correctly excludes expected `CURRENT_STATE.md` writes but does not exclude:
- New files added to `handoffs/ARCHIVE/` (session-summary archival)
- The `??` status (untracked) for files that were moved from INBOX to ARCHIVE

## Proposed fix class

- Extend the dirty-tree guard exclusion list to also ignore new untracked files in `handoffs/ARCHIVE/`.
- Or: check if the only diff is untracked ARCHIVE files before writing the URGENT.

## Disposition for existing URGENT

`runtime/.handoff/URGENT-supervisor-reflection-dirty-tree.md` is a false positive. The attended session may delete it without further investigation.
