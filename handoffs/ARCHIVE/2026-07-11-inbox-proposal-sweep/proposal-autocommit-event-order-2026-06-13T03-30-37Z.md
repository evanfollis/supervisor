---
from: synthesis-translator
to: general
date: 2026-06-13T03:30:37Z
priority: high
task_id: synthesis-autocommit-event-order
source_synthesis: /opt/workspace/runtime/.meta/cross-cutting-2026-06-13T03-26-25Z.md
source_proposal: Proposal 1 — P-autocommit-event-order
---

# P-autocommit-event-order (FR-D) — Fix autocommit event ordering

**Status:** 3rd synthesis cycle at #1 priority. Now at the >3-cycle flag threshold.
**Leverage:** Maximum. This is the sole remaining tick blocker. <10 min, zero credentials, zero risk.

## The problem

The supervisor-autocommit script emits a telemetry event AFTER the `git commit`, which dirties the tree for the next automation step:

```
Cycle N:
  git commit → emit_event → tree dirty for next tick
Cycle N+1:
  supervisor-tick fires, finds dirty tree, skips
  (repeat)
```

This is a 14+ cycle regression documented across C93, C94, C95.

## What to fix

File: `supervisor/scripts/lib/supervisor-autocommit.sh`, lines 79-84.

**Current (broken):**
```bash
git -C "$SUP" \
  -c user.email='autocommit@workspace.local' \
  -c user.name='supervisor-autocommit' \
  commit --quiet -m "autocommit ${ISO_NOW}: Tier-A governance artifacts
...
agent: autocommit" || { log "commit failed"; emit_event "session_reflected" "autocommit commit failed"; exit 1; }

NEW_SHA=$(git -C "$SUP" rev-parse HEAD)
git -C "$SUP" branch -f "$BRANCH" "$NEW_SHA"

emit_event "session_reflected" "autocommit: committed Tier-A on current branch and marked $BRANCH (sha=${NEW_SHA:0:12})"
log "committed Tier-A writes on current branch and marked $BRANCH (sha=${NEW_SHA:0:12})"
```

**Fixed (option B — emit before, log SHA after):**
```bash
# Emit the event BEFORE git commit so the tree is not dirtied
emit_event "session_reflected" "autocommit: committing Tier-A on current branch"

# Stage and commit
git -C "$SUP" add events/ 2>/dev/null || true
git -C "$SUP" \
  -c user.email='autocommit@workspace.local' \
  -c user.name='supervisor-autocommit' \
  commit --quiet -m "autocommit ${ISO_NOW}: Tier-A governance artifacts
...
agent: autocommit" || { log "commit failed"; emit_event "session_reflected" "autocommit commit failed"; exit 1; }

# Record the commit SHA
NEW_SHA=$(git -C "$SUP" rev-parse HEAD)
git -C "$SUP" branch -f "$BRANCH" "$NEW_SHA"
log "committed Tier-A writes on current branch and marked $BRANCH (sha=${NEW_SHA:0:12})"
```

## Why this matters

Every 12h without this fix:
- +1 supervisor tick skipped
- +12h verified-state staleness
- +1 dispatch obligation breach
- Reflection loops degrade further

The governance clock has not advanced since Jun 9 (81h stale verified-state). Every cycle adds noise to the diagnostic layer.

## Verification before action (required)

- Check `git log --oneline -5` on supervisor. Confirm no recent commits landing this fix via another path.
- Read `supervisor/scripts/lib/supervisor-autocommit.sh` lines 79-84. Confirm the current code has event AFTER commit.
- If already fixed, write a completion report: "Already landed at commit <SHA> / verified in-file."

## Acceptance criteria

- The event emission is moved BEFORE the git commit.
- The `events/` directory is staged before commit.
- The commit message and log message remain unchanged.
- No other behavioral changes.
- Change committed with clear message explaining the fix and the synthesis source.
- Completion report written to `runtime/.handoff/general-supervisor-synthesis-autocommit-event-order-complete-<iso>.md` pointing back to this handoff.

## Expected impact

Takes effect on the next autocommit cycle (~2h from deployment). Should unblock:
- supervisor tick (currently stuck in loop)
- verified-state refresh
- governance dispatch automation
- all downstream recommendations in synthesis

This is the blocking item for all other workspace recovery work.
