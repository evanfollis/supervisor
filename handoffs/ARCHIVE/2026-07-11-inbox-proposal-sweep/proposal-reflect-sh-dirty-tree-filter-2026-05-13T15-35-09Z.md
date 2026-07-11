---
from: synthesis-translator
to: general
date: 2026-05-13T15:35:09Z
priority: high
task_id: synthesis-proposal-2-reflect-dirty-tree
source_synthesis: /opt/workspace/runtime/.meta/cross-cutting-2026-05-13T15-26-05Z.md
source_proposal: "Proposal 2 — Exclude handoffs/ARCHIVE/ from reflect.sh dirty-tree check"
---

# Fix reflect.sh dirty-tree false positives from concurrent autocommit

## Summary

The `reflect.sh` safety net compares `git status` before and after reflection sessions to detect unexpected mutations. However, the autocommit timer deposits session-summary files in `handoffs/ARCHIVE/` concurrently with reflections, creating false-positive URGENT notifications. This pattern recurs (last occurred May 2; flagged again May 13), generating noise without adding signal.

## The problem

- **False-positive trigger:** Concurrent autocommit deposits untracked files in `handoffs/ARCHIVE/` between the before/after `git status` snapshots in reflect.sh.
- **Evidence:** May 13 14:33Z supervisor reflection fired `URGENT-supervisor-reflection-dirty-tree.md` showing only new untracked `handoffs/ARCHIVE/` files as the delta.
- **Recurrence:** Same file path fired previously on May 2 (`.done` exists).
- **Impact:** Degrades signal quality of the safety net; dilutes legitimate mutation detection with known-concurrent background traffic.

## The fix

In `/opt/workspace/supervisor/scripts/lib/reflect.sh`, within the dirty-tree check logic (look for `git status` snapshots and comparison), filter out `handoffs/ARCHIVE/` from both before and after snapshots before comparing:

```bash
# Approximately at the dirty-tree comparison logic in reflect.sh:
# (After taking the "after" snapshot, before comparing to "before")

BEFORE_FILTERED=$(echo "$BEFORE_STATUS" | grep -v '^?? handoffs/ARCHIVE/')
AFTER_FILTERED=$(echo "$AFTER_STATUS" | grep -v '^?? handoffs/ARCHIVE/')

if [ "$BEFORE_FILTERED" != "$AFTER_FILTERED" ]; then
  # ... emit URGENT with the filtered diff ...
fi
```

Alternative: check `git diff --name-only HEAD` (tracked files only) instead of `git status`, which would exclude untracked files entirely. The grep filter is less disruptive if reflect.sh intends to detect untracked file creation by the reflection itself.

## Why this works

- **Eliminates known-concurrent source:** Autocommit deposits are structural, expected, and orthogonal to reflection mutations.
- **Preserves real signal:** The filtered safety net still detects actual reflection-caused mutations (uncommitted code changes, new tracked files).
- **Targeted:** Only filters one path; does not weaken the detector globally.

## Verification before action (required)

- Read `/opt/workspace/supervisor/scripts/lib/reflect.sh`. Locate the dirty-tree check (search for `git status` comparison or similar).
- Verify the current implementation captures both before/after snapshots in variables.
- Check if the filtering logic is already present (if so, report "already implemented" with commit reference).

## Acceptance criteria

- Filter logic added to `reflect.sh` dirty-tree check, explicitly excluding `handoffs/ARCHIVE/` (or equivalent untracked-file exclusion if using `git diff` alternative).
- Commit with a clear message (e.g., "Filter handoffs/ARCHIVE from reflect.sh dirty-tree check to suppress concurrent-autocommit noise").
- Re-test: trigger a reflection manually and verify no false-positive URGENT fires when autocommit deposits session summaries concurrently.
- Completion report confirms the fix lands and testing shows no false positives.

## Escalation

URGENT if:
- The dirty-tree check has changed implementation significantly since this proposal was written (look for recent commits touching reflect.sh).
- Filtering `handoffs/ARCHIVE/` introduces new failure modes (e.g., actual mutations in that path would now be hidden — unlikely but should be verified).
