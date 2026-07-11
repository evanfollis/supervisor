---
from: synthesis-translator
to: general
date: 2026-05-28T03:27:57Z
priority: high
task_id: synthesis-dirty-tree-whitelist
source_synthesis: /opt/workspace/runtime/.meta/cross-cutting-2026-05-28T03-24-25Z.md
source_proposal: C61 Proposal 2 (STRUCTURAL — prevents P1 recurrence)
---

# Dirty-tree whitelist

**Status:** Open, **3 cycles**. `supervisor/scripts/lib/supervisor-tick.sh`. Exclude known-autocommit files from dirty-tree check. Eliminates the failure class.

## Context

Once P1 (expand autocommit scope) restores tick operation, this prevents P1's failure from recurring. The dirty-tree check blocks tick execution when modified files exist in the repo. But autocommit writes to files like `events/supervisor-events.jsonl`, which means tick will fail immediately after autocommit runs, until the next autocommit cycle that includes those modified files.

A whitelist in the tick script that excludes known-autocommit files from the dirty-tree check eliminates this entire failure class: tick can proceed as long as the only dirty files are ones autocommit is responsible for managing.

## Verification before action (required)

- Check if `supervisor-tick.sh` already has a whitelist mechanism
- Verify P1 (autocommit scope expansion) has landed before applying this
- If already present, write a completion report stating "already landed" and do not re-apply

## Acceptance criteria

- `supervisor/scripts/lib/supervisor-tick.sh` includes a dirty-tree whitelist excluding files in the autocommit scope
- Tick continues to block on genuine dirty state (unexpected modifications) but allows autocommit files
- Change committed with message explaining the failure-class elimination

## Escalation

URGENT if:
- The whitelist causes tick to proceed when it shouldn't (too permissive)
- Dirty state detection loses accuracy as a safety mechanism
