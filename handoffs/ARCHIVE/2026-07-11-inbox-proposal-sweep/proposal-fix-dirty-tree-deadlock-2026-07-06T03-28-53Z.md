---
from: synthesis-translator
to: general
date: 2026-07-06T03:28:53Z
priority: critical
task_id: synthesis-fix-dirty-tree-deadlock
source_synthesis: /opt/workspace/runtime/.meta/cross-cutting-2026-07-06T03-24-44Z.md
source_proposal: P4 — Fix dirty-tree deadlock
---

# Fix dirty-tree deadlock

## Proposal

**Type:** `supervisor-autocommit.sh:79-84` — detect 2-behind state and stage events continuously so the tree is never dirty when the tick checks.

**Context:** The supervisor tick (primary autonomous actuator) has been unable to run for 41+ synthesis cycles (~20.5 days). The dirty-tree check blocks execution. The autocommit script can be modified to prevent the tree from ever being dirty at check time.

**Implementation:** Modify `supervisor-autocommit.sh:79-84` to detect the 2-behind state and keep the working tree clean by staging events.jsonl continuously (before autocommit checks for uncommitted changes).

**Blast radius:** Supervisor only. Unblocks the tick (primary autonomous actuator).

**BLOCKER NOTICE:** This fix is blocked on a principal authorization: `git pull --rebase` on the supervisor repo (537 ahead, 2 behind origin/main). The script fix will only be effective after that rebase is completed. The fix is ready to implement; the rebase is a separate principal decision. See "Critical path for governance recovery" in the source synthesis.

## Verification before action (required)

- Check `/opt/workspace/supervisor/scripts/lib/supervisor-autocommit.sh` lines 79–84 for the current autocommit logic.
- Verify the 2-behind state: `git -C /opt/workspace/supervisor log --oneline origin/main..HEAD 2>/dev/null | wc -l` should be 0 (will be after rebase).
- Check if the tree is currently dirty: `git -C /opt/workspace/supervisor status --porcelain` should be empty after fix is active.
- If the fix is already in place, verify the dirty-tree prevention logic is operational.

## Acceptance criteria

Assuming the rebase has been authorized and completed:
- `supervisor-autocommit.sh` is modified to detect the 2-behind state and stage events.jsonl continuously.
- Logic prevents the working tree from being dirty when the tick's check runs.
- Commit message: "Fix dirty-tree deadlock in supervisor-autocommit — stage events continuously to prevent dirty checks"
- Test: Run `supervisor-tick.sh` manually and verify it executes (no dirty-tree skip).
- Completion report at `runtime/.handoff/general-complete-fix-dirty-tree-deadlock-<iso>.md` noting:
  - Whether the rebase was completed first (required before this fix is effective)
  - Whether the tick now executes without dirty-tree skips
  - Any remaining blockers

## Escalation

URGENT if:
- The rebase has still not been authorized. Do not force-apply this fix without the rebase — it will not solve the deadlock alone.
- The supervisor tree is in an unexpected state (unexpected files, branches, etc.). Escalate with the unexpected state details.
- The script modification requires different logic than described. Escalate with the specifics.
