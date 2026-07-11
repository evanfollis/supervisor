---
from: synthesis-translator
to: general
date: 2026-06-16T03:27:01Z
priority: critical
task_id: synthesis-p-autocommit-event-order
source_synthesis: /opt/workspace/runtime/.meta/cross-cutting-2026-06-16T03-23-07Z.md
source_proposal: 1. P-autocommit-event-order
---

# P-autocommit-event-order

**Type:** Shared primitive fix.
**File:** `supervisor/scripts/lib/supervisor-autocommit.sh`, lines 79-84.

**What:** Reorder so the completion event is emitted and staged BEFORE the `git commit`, not after. Unchanged from C93–C100:

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

**Blast radius:** Supervisor only. Automatic. No other project affected.

**Status:** 9th synthesis cycle. <10 min, zero credentials, zero risk. FR-D action handoff on disk ~36.9h (48h threshold at ~2026-06-16T14:26Z).

**Root cause:** `emit_event` at `supervisor-autocommit.sh:84` fires after `git commit`, dirtying the tree for the next tick. This blocks all downstream tick execution and is the single point of failure for the governance chain.

**Failure class:** Self-referential automation pollution.

## Verification before action (required)

- Run `cd supervisor && git log --oneline -10 -- scripts/lib/supervisor-autocommit.sh`. Check if this fix has already landed via another path.
- Read `/opt/workspace/supervisor/scripts/lib/supervisor-autocommit.sh` around lines 71-85. Confirm `emit_event` is called AFTER `git commit` (broken state).
- If already fixed, write a completion report stating "already landed at commit <SHA>" rather than re-applying.

## Acceptance criteria

- The `emit_event` call is moved BEFORE `git commit` and the `events/` directory is added to the staging area in the same transaction.
- No additional `emit_event` call happens after `git commit` (remove the current line 84).
- Change committed with clear message explaining the fix and the synthesis source.
- Completion report at `supervisor/handoffs/INBOX/general-supervisor-synthesis-p-autocommit-event-order-complete-<iso>.md` pointing back to this handoff and the source synthesis.

## Escalation

URGENT if:
- The fix has already landed by another path and this handoff is obsolete.
- The reordering conflicts with another part of the script logic.
