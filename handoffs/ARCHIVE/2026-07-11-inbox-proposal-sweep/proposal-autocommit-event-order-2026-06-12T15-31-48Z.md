---
from: synthesis-translator
to: general
date: 2026-06-12T15:31:48Z
priority: high
task_id: synthesis-autocommit-event-order
source_synthesis: /opt/workspace/runtime/.meta/cross-cutting-2026-06-12T15-27-51Z.md
source_proposal: 1. P-autocommit-event-order (carry from C93 — 2nd cycle, HIGHEST PRIORITY)
---

# P-autocommit-event-order (FR-D fix)

**Rank: Highest Priority — 2nd consecutive synthesis cycle carrying this.**

## The Problem

The supervisor autocommit script has a self-referential pollution bug (FR-D): the completion event is emitted AFTER the git commit, which dirties the working tree by adding the event to the events/ directory. This causes the subsequent tick to find the tree dirty and skip, preventing governance advancement.

The pattern repeats mechanically:
1. autocommit fires
2. commits events/ into git
3. EMITS event to events/ (post-commit) ← dirties tree
4. tick fires 26 min later
5. finds events/ dirty
6. skips

This has occurred 6+ consecutive times in the current window alone, with verified-state.md now ~70h stale.

## The Fix

**File:** `supervisor/scripts/lib/supervisor-autocommit.sh`, lines 79–84 (current).

Reorder so the completion event is emitted and staged BEFORE the git commit:

```bash
# Current (broken):
git -C "$SUP" commit ...  # lines 71-79
NEW_SHA=$(git -C "$SUP" rev-parse HEAD)
git -C "$SUP" branch -f "$BRANCH" "$NEW_SHA"
emit_event "session_reflected" "autocommit: committed Tier-A on current branch and marked $BRANCH (sha=${NEW_SHA:0:12})"

# Fixed:
emit_event "session_reflected" "autocommit: committed Tier-A on current branch"
git -C "$SUP" add events/ 2>/dev/null || true
git -C "$SUP" commit ...  # event is now part of the committed state
NEW_SHA=$(git -C "$SUP" rev-parse HEAD)
git -C "$SUP" branch -f "$BRANCH" "$NEW_SHA"
emit_event "session_reflected" "autocommit: committed Tier-A on current branch and marked $BRANCH (sha=${NEW_SHA:0:12})"
log "committed Tier-A writes on current branch and marked $BRANCH (sha=${NEW_SHA:0:12})"
```

**Note:** The pre-commit event cannot include the SHA since the commit hasn't happened yet. The post-commit event includes it. Both events are necessary to bookend the operation.

## Workspace Impact

- **Blast radius:** Supervisor only. Takes effect next autocommit cycle.
- **Effort:** <10 minutes
- **Credentials:** Zero
- **Risk:** Zero — this is a pure reordering that eliminates the self-pollution
- **Leverage:** Maximum. This is the sole blocker for tick advancement, governance automation, and verified-state refresh.

## Verification Before Action

```bash
# Confirm the current (broken) order:
git log --oneline -20 | grep -E "24ac3c6|P2|P-reflect-prompt"
# Should show recent P2 landing but no FR-D fix

# Check supervisor-autocommit.sh lines 71-85:
sed -n '71,85p' supervisor/scripts/lib/supervisor-autocommit.sh
# Should show: commit → get SHA → emit event (broken order)
```

## Acceptance Criteria

- The emit event for "autocommit: committed Tier-A" is called BEFORE `git commit`
- The event is staged with `git add events/` before commit
- The post-commit emit that includes the SHA remains after the commit
- Next autocommit cycle succeeds without dirtying the tree
- Subsequent tick does NOT skip
- Commit message clearly references this FR-D fix and the synthesis cycle

## Escalation

URGENT if:
- The fix is conditional on a decision not yet recorded in `supervisor/decisions/`
- Another PR/commit lands the same fix by a different path while this handoff is open
- The proposed fix creates a new issue with event sequencing (verify with `git log -p` on the next cycle's commit to ensure events are included cleanly)

---

**Why this matters now:** Every hour without this fix is pure waste. The synthesis cycle rate (12h) and tick advancement rate (disabled) are now decoupled. This is the single item blocking all downstream automation.
