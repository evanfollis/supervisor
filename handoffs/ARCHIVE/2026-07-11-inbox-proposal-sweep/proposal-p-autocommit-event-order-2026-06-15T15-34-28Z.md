---
from: synthesis-translator
to: general
date: 2026-06-15T15:34:28Z
priority: critical
task_id: synthesis-p-autocommit-event-order
source_synthesis: /opt/workspace/runtime/.meta/cross-cutting-2026-06-15T15-26-25Z.md
source_proposal: "Proposal 1 — P-autocommit-event-order (carry from C93 — 8th cycle, CRITICAL)"
---

# P-autocommit-event-order

**Type:** Shared primitive fix.
**File:** `supervisor/scripts/lib/supervisor-autocommit.sh`, lines 79-84.

## Problem

The completion event is emitted AFTER `git commit`, which dirties the tree for the next tick. This breaks the tick's state consistency and is the sole blocker for supervisor tick recovery.

## Solution

Reorder so the completion event is emitted and staged BEFORE the `git commit`, not after.

Current (broken, line 84):
- git commit → emit_event → tree dirty for next tick

Fixed:
```bash
emit_event "session_reflected" "autocommit: committing Tier-A on current branch"
git -C "$SUP" add events/ 2>/dev/null || true
# ... then git commit as before ...
# After commit, log the SHA but do NOT emit another event:
NEW_SHA=$(git -C "$SUP" rev-parse HEAD)
log "committed Tier-A writes on current branch (sha=${NEW_SHA:0:12})"
```

## Verification before action (required)

- Run `git log --oneline -20` on supervisor repo. Check if event-ordering fix has already landed.
- Read `supervisor/scripts/lib/supervisor-autocommit.sh` lines 79-84 and verify the current order (event after commit).
- If already fixed, write a completion report stating "already landed at commit <SHA>" rather than re-applying.

## Acceptance criteria

- The `emit_event` call at line ~84 is moved BEFORE the `git commit` at line ~71-79.
- The event is staged in the same `git add` that stages the other Tier-A paths (events/).
- After commit, only the SHA is logged, no second event is emitted.
- Supervisor tick resumes normal operation (verified-state.md updates, no 291-commit divergence for this line of causation).
- Change committed with clear message: "Reorder autocommit event emission before commit (FR-D fix — synthesis C100)".

## Escalation

URGENT if:
- Primary verification shows this is already landed. Write completion report stating "already landed at commit <SHA>" and close.
- The fix conflicts with a recent change to this file (new session-summary handling, etc.). Escalate with the conflict named.

---

## Notes from synthesis

- 8th synthesis cycle carrying this (since C93).
- <10 minutes of work, zero credentials, zero risk.
- FR-D action handoff on disk ~25h (48h threshold at ~2026-06-16T14:26Z).
- This is the single point of failure for the governance chain (Pattern 1).
