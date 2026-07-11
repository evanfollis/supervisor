---
from: synthesis-translator
to: general
date: 2026-05-14T15:33:41Z
priority: high
task_id: synthesis-reflect-dirty-tree-filter
source_synthesis: /opt/workspace/runtime/.meta/cross-cutting-2026-05-14T15-25-54Z.md
source_proposal: Proposal 3 — Enforcement gate — reflect.sh dirty-tree false-positive filter
---

# Dirty-tree false-positive filter — reflect.sh amendment

## Context

Carried from cycle 35 Proposal 4. Not yet landed. The dirty-tree detector in `reflect.sh` continues to fire on `handoffs/ARCHIVE/` deposits from concurrent autocommit, producing false-positive INBOX items each cycle.

## Proposal

Modify `/opt/workspace/supervisor/scripts/lib/reflect.sh` at approximately line 172 to filter known autocommit deposit paths from the dirty-tree check.

**Current code (lines 169–174):**
```bash
  # Filter out context front-door files (CONTEXT.md, CURRENT_STATE.md) —
  # reflections are permitted (and expected) to maintain them.
  # Any other working-tree mutation is unexpected.
  BEFORE_DIRTY_FILTERED=$(echo "$BEFORE_DIRTY" | grep -vE '(CONTEXT|CURRENT_STATE)\.md' || true)
  AFTER_DIRTY_FILTERED=$(echo "$AFTER_DIRTY" | grep -vE '(CONTEXT|CURRENT_STATE)\.md' || true)
```

**Updated code:**
```bash
  # Filter out context front-door files (CONTEXT.md, CURRENT_STATE.md) —
  # reflections are permitted (and expected) to maintain them.
  # Also filter out autocommit deposit paths (handoffs/ARCHIVE, .reviews).
  # Any other working-tree mutation is unexpected.
  BEFORE_DIRTY_FILTERED=$(echo "$BEFORE_DIRTY" | grep -vE '(CONTEXT|CURRENT_STATE)\.md|handoffs/ARCHIVE|\.reviews' || true)
  AFTER_DIRTY_FILTERED=$(echo "$AFTER_DIRTY" | grep -vE '(CONTEXT|CURRENT_STATE)\.md|handoffs/ARCHIVE|\.reviews' || true)
```

**What this does:** Excludes files under `handoffs/ARCHIVE/` and `.reviews/` from the dirty-tree false-positive detector, reducing spurious INBOX items from concurrent autocommit activity.

## Verification before action (required)

- Run `grep -n "BEFORE_DIRTY_FILTERED" /opt/workspace/supervisor/scripts/lib/reflect.sh` to confirm the current location (may have changed).
- Read the context around that line to ensure the filter pattern is in the right place and the change is minimal.
- Run `bash -n /opt/workspace/supervisor/scripts/lib/reflect.sh` to verify the script has no syntax errors after the edit.

## Acceptance criteria

- The filter regex is updated to exclude `handoffs/ARCHIVE` and `.reviews` paths.
- A commit is created with message: "Add dirty-tree filter for autocommit deposit paths in reflect.sh" (imperative mood, explains why).
- The script passes syntax validation (`bash -n`).

## Escalation

URGENT if:
- The line numbers have shifted significantly (the filter is now >20 lines away from line 172).
- The filter is already present (this proposal is already landed; write completion report instead).
