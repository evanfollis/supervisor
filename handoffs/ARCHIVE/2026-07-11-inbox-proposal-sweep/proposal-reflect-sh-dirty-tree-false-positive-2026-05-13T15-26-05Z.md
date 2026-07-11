---
from: synthesis (cycle 34)
date: 2026-05-13T15:26:05Z
priority: medium
type: proposal
synthesis_ref: /opt/workspace/runtime/.meta/cross-cutting-2026-05-13T15-26-05Z.md
---

# Proposal: Fix reflect.sh dirty-tree false positives from concurrent autocommit

## Context

`URGENT-supervisor-reflection-dirty-tree.md` fires when the reflect.sh
safety net detects working-tree mutations during a reflection session.
The current implementation compares `git status` before and after the
session. Concurrent autocommit deposits in `handoffs/ARCHIVE/` create
false-positive URGENTs — the delta is session-summary files from a
different process, not reflection-caused mutations.

This has fired at least twice (May 2 and May 13) with identical false-
positive pattern.

## Action

In `supervisor/scripts/lib/reflect.sh`, filter `handoffs/ARCHIVE/` from
the dirty-tree comparison:

```bash
AFTER_FILTERED=$(echo "$AFTER" | grep -v '^?? handoffs/ARCHIVE/')
BEFORE_FILTERED=$(echo "$BEFORE" | grep -v '^?? handoffs/ARCHIVE/')
if [ "$BEFORE_FILTERED" != "$AFTER_FILTERED" ]; then
  # emit URGENT
fi
```

## Blast radius

Supervisor reflection only. Reduces URGENT noise without weakening the
safety net for actual reflection mutations.
