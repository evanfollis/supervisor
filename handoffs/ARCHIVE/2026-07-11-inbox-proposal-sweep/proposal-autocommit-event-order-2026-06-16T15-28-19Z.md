---
from: synthesis-translator
to: general
date: 2026-06-16T15:28:19Z
priority: critical
task_id: synthesis-autocommit-event-order
source_synthesis: /opt/workspace/runtime/.meta/cross-cutting-2026-06-16T15-24-30Z.md
source_proposal: 1. P-autocommit-event-order (carry from C93 — 10th cycle, CRITICAL, 48h threshold crossed)
---

# P-autocommit-event-order: Fix FR-D event emission ordering

## Full proposal from synthesis

**Type:** Shared primitive fix.
**File:** `supervisor/scripts/lib/supervisor-autocommit.sh`, lines 79-84.

**What:** Reorder so the completion event is emitted and staged BEFORE
the `git commit`, not after. Unchanged from C93–C101:

```bash
# Current (broken, line 84):
#   git commit → emit_event → tree dirty for next tick

# Fixed:
emit_event "session_reflected" "autocommit: committing Tier-A on current branch"
git -C "$SUP" add events/ 2>/dev/null || true
# ... then git commit as before ...
# After commit, log the SHA but do NOT emit another event:
NEW_SHA=$(git -C "$SUP" rev-parse HEAD)
log "committed Tier-A writes on current branch (sha=${NEW_SHA:0:12})"
```

**Prerequisite (NEW):** Resolve supervisor branch divergence first.
`git pull --rebase origin main` or equivalent, then fix, then push.

**Blast radius:** Supervisor only. Automatic. No other project affected.

**Status:** 10th synthesis cycle. <10 min (+ 5 min for branch merge).
Action handoff at `runtime/.handoff/general-frd-action-2026-06-14T14-26-40Z.md`
has crossed the 48h threshold.

## Verification before action (required)

- Verify the branch divergence: `git -C /opt/workspace/supervisor status` should show commits ahead AND behind origin.
- Verify the broken state: `git -C /opt/workspace/supervisor log --oneline -3` to confirm current HEAD is the autocommit.sh being referenced.
- If the patch is already applied (event emission before commit), skip this handoff and write a completion report stating "already landed."

## Acceptance criteria

1. Resolve supervisor branch divergence: `git -C /opt/workspace/supervisor pull --rebase origin main` (or equivalent merge/rebase strategy).
2. Apply the patch to `supervisor/scripts/lib/supervisor-autocommit.sh`:
   - Move the `emit_event` call to execute BEFORE the `git commit` (not after).
   - Add `git -C "$SUP" add events/` after emit_event to stage the event file.
   - Remove any duplicate event emission after the commit.
   - Keep the log statement after commit (for SHA reporting only).
3. Commit with message: "Fix FR-D: emit completion event before commit, not after"
4. Push to origin/main.
5. Verify tick recovery: next 02:xx or 14:xx UTC tick should proceed normally without empty-tree pollution.

## Escalation

URGENT if:
- Branch divergence resolution fails (merge conflict in supervisor or unexpected history shape).
- The fix is applied but tick still fails — escalate with the tick log snippet.
- This proposal's prerequisite (branch divergence) is already resolved by a different path. Confirm via git log before proceeding.

