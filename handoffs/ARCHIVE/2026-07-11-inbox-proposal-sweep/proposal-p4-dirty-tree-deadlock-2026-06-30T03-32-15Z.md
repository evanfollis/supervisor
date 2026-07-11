---
from: synthesis-translator
to: general
date: 2026-06-30T03:32:15Z
priority: high
task_id: synthesis-p4-dirty-tree-deadlock
source_synthesis: /opt/workspace/runtime/.meta/cross-cutting-2026-06-29T15-27-11Z.md
source_proposal: P4 - Fix dirty-tree deadlock
---

# P4: Fix dirty-tree deadlock in supervisor-autocommit.sh

## Full Proposal (from C114)

**Status in C114:** 28th cycle carry-forward. Requires the 2-behind rebase first (`git pull --rebase` on supervisor). The rebase has been requested in **14 consecutive synthesis cycles** (C99–C114) without authorization or recorded deferral.

**Blocked on:** `git pull --rebase` on `/opt/workspace/supervisor` to resolve 2 commits behind origin/main.

**Target fix location:** `/opt/workspace/supervisor/scripts/lib/supervisor-autocommit.sh` lines 79-84.

**Current state (from C114):** The dirty-tree deadlock occurs because autocommit writes are made before the tick's event emission. The order must be reversed to prevent the working tree from remaining dirty when the supervisor-tick loop depends on a clean state.

**Related evidence (from C114 reflection):** The autocommit-only case is producing tick-skip pairs (~6 each in recent windows). The tick cannot proceed because the tree is dirty, the autocommit happens, the tick still sees the tree as dirty for its own pre-flight checks, and the deadlock recurs on the next tick cycle.

**Blast radius:** Supervisor only. Unblocks: tick loop, verified-state refresh, dispatch obligation enforcement, governance automation.

**Why this is critical:** This is the primary blocker preventing the governance infrastructure from functioning. Resolving the 2-behind divergence + applying this fix would unblock the entire supervisor control plane.

## Verification before action (required)

- Run `git log --oneline -20` on `/opt/workspace/supervisor`. Check if this fix has already landed via another path (commit message would reference P4, dirty-tree, or autocommit-event-order).
- Run `git log -1 --format=%H` on `/opt/workspace/supervisor` and compare against `git ls-remote origin main | awk '{print $1}'` to check the 2-behind state. If the supervisor is not 2 behind, the rebase prerequisite may have already been resolved.
- Read `/opt/workspace/supervisor/scripts/lib/supervisor-autocommit.sh` lines 79-84. Check the order of operations (whether `emit_event` happens before or after the autocommit).
- If the fix is already present and supervisor is not 2-behind, write a completion report stating "already landed" and close.

## Acceptance criteria

1. **Prerequisite: Resolve supervisor divergence**
   - Run `git pull --rebase` on `/opt/workspace/supervisor` to bring it current with origin/main
   - Resolve any merge conflicts if they occur
   - Verify `git log -1` now shows supervisor at the same commit as `git ls-remote origin main`

2. **Fix dirty-tree deadlock**
   - Review lines 79-84 of `supervisor-autocommit.sh` to understand the current event/commit order
   - Reorder the operations so that event emission (telemetry) happens AFTER the autocommit, not before
   - This prevents the working tree from appearing dirty when the tick's next pre-flight check runs
   - Change committed with message: "Fix dirty-tree deadlock in supervisor autocommit — emit events after commit to keep tree clean for tick loop" (or similar — explain the why)

3. **Post-fix verification**
   - Run the supervisor-tick loop and observe that it no longer gets stuck in tick-skip pairs
   - Verify that `git status` returns clean after autocommit cycles
   - Check `/opt/workspace/supervisor/events/supervisor-events.jsonl` for a successful `session_reflected` event from the autocommit

4. **Completion report**
   - Post to `/opt/workspace/supervisor/handoffs/INBOX/general-p4-dirty-tree-deadlock-complete-<iso>.md`
   - Include evidence: the commit SHA from the rebase, the commit SHA of the autocommit fix, and a sample of clean `git status` output post-fix

## Escalation

URGENT if:
- Primary verification reveals the 2-behind divergence has already been resolved. Check whether the autocommit fix has also landed. If yes, write "obsolete — already landed" and close.
- The rebase fails with merge conflicts. Escalate with the conflict output and ask the principal or an attended session to resolve it.
- Lines 79-84 of `supervisor-autocommit.sh` have been substantially restructured so the proposed fix location no longer applies. Escalate with the current structure of that block.
- After applying the fix, the tick loop still gets stuck in skip pairs. Escalate with the evidence (recent supervisor-events.jsonl entries) and ask for deeper investigation.
