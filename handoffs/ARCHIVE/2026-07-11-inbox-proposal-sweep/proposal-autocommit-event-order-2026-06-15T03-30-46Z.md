---
from: synthesis-translator
to: general
date: 2026-06-15T03:30:46Z
priority: critical
task_id: synthesis-p-autocommit-event-order
source_synthesis: /opt/workspace/runtime/.meta/cross-cutting-2026-06-15T03-27-01Z.md
source_proposal: Proposal 1 — P-autocommit-event-order
---

# P-autocommit-event-order (carry from C93 — 7th cycle, CRITICAL)

**Type:** Shared primitive fix.
**File:** `supervisor/scripts/lib/supervisor-autocommit.sh`, lines 79-84.

## What

Reorder so the completion event is emitted and staged BEFORE the `git commit`, not after. Identical to C93–C98:

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

## Blast radius

Supervisor only. Automatic. No other project affected.

## Verification before action (required)

Run `git log --oneline -20` on supervisor. Check if this fix has been applied via a recent commit.

Read `/opt/workspace/runtime/.handoff/general-frd-action-2026-06-14T14-26-40Z.md` for the exact diff to apply — it contains the detailed patch with clear before/after.

## Acceptance criteria

- The event emission is moved to BEFORE `git add` (so it's included in the commit transaction)
- Post-commit `emit_event` call is removed
- Change committed with clear message referencing the synthesis source and FR-D deadlock
- Completion report at `runtime/.handoff/general-synthesis-p-autocommit-event-order-complete-<iso>.md` pointing back to this handoff

## Escalation

URGENT if:
- The fix has already landed (check supervisor git log for similar changes in recent commits)
- The proposal conflicts with other pending changes to the autocommit script
