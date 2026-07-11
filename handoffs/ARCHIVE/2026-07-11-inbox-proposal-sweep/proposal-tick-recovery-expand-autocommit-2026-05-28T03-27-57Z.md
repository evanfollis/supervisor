---
from: synthesis-translator
to: general
date: 2026-05-28T03:27:57Z
priority: high
task_id: synthesis-tick-recovery-expand-autocommit
source_synthesis: /opt/workspace/runtime/.meta/cross-cutting-2026-05-28T03-24-25Z.md
source_proposal: C61 Proposal 1 (IMMEDIATE — tick recovery)
---

# Expand autocommit scope

**Status:** Open, **3 cycles**. `supervisor/scripts/lib/supervisor-autocommit.sh`. Add `events/supervisor-events.jsonl` + clear test artifacts. Unblocks tick loop. <5 min fix.

## Context

The supervisor tick has been halted since ~16:47Z on 2026-05-26 — now ~36 hours. Root cause: `events/supervisor-events.jsonl` is modified by tick, excluded from autocommit scope, and the dirty-tree check blocks the next tick. Test artifacts remain in the dirty set. Adding these files to the autocommit scope immediately unblocks the tick loop and stops the cascading skip-escalation events being generated every 2 hours.

This is direct cause of tick halt. Immediate fix.

## Verification before action (required)

- Check if autocommit.sh already includes `events/supervisor-events.jsonl` in its scope
- Verify the tick halt is still active: `cat supervisor-reflection-2026-05-28T02-22-25Z.md` should show tick halt at 34h+
- If tick is already running, write a completion report stating "already landed" and do not re-apply

## Acceptance criteria

- `events/supervisor-events.jsonl` is added to the autocommit scope in `supervisor/scripts/lib/supervisor-autocommit.sh`
- Test artifacts (if present) are cleared or excluded
- Tick resumes producing regular heartbeats
- Change committed with message explaining the synthesis source and tick recovery

## Escalation

URGENT if:
- Tick remains halted after change — investigate concurrent blocking conditions (dirty-tree check, other system-level holds)
- The events file is being actively written during autocommit — may need locking or transactional semantics
