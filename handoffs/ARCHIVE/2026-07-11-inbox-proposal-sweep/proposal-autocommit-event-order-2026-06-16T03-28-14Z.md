---
from: synthesis-translator
to: general
date: 2026-06-16T03:28:14Z
priority: critical
task_id: synthesis-autocommit-event-order
source_synthesis: /opt/workspace/runtime/.meta/cross-cutting-2026-06-16T03-23-07Z.md
source_proposal: 1. P-autocommit-event-order (carry from C93 — 9th cycle, CRITICAL)
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

## Verification before action (required)

- Run `git log --oneline -20` on `/opt/workspace/supervisor` (or the repo containing the script). Check if this proposal has already landed via a commit with a message referencing the event-order fix.
- Read `supervisor/scripts/lib/supervisor-autocommit.sh` lines 79-84. Check if `emit_event` is already called BEFORE `git commit` (fixed state) or AFTER (broken state).
- If either check shows the fix is already in place, write a completion report stating "already landed at commit <SHA>" rather than re-applying.

## Acceptance criteria

- Lines 79-84 in `supervisor/scripts/lib/supervisor-autocommit.sh` are reordered so `emit_event` fires and `events/` is staged before `git commit`.
- Change committed with a message explaining the root cause (event fires after commit, dirtying tree for next tick).
- Completion report at `supervisor/handoffs/ARCHIVE/<iso>/general-autocommit-event-order-complete.md` pointing back to this handoff and the source synthesis.

## Escalation

URGENT if:
- Verification reveals the fix is already applied. Write a brief completion report saying "already landed" and close without re-applying.
- The proposal conflicts with more recent infrastructure changes. Surface the conflict with specifics.
