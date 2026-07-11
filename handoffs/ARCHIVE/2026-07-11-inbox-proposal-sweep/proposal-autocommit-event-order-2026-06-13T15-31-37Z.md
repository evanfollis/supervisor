---
from: synthesis-translator
to: general
date: 2026-06-13T15:31:37Z
priority: critical
task_id: synthesis-p-autocommit-event-order
source_synthesis: /opt/workspace/runtime/.meta/cross-cutting-2026-06-13T15-27-25Z.md
source_proposal: "Proposal 1 — P-autocommit-event-order (4th cycle, PAST >3-CYCLE FLAG)"
---

# P-autocommit-event-order

**Type:** Shared primitive fix  
**File:** `supervisor/scripts/lib/supervisor-autocommit.sh`, lines 79-84  
**Target:** Supervisor only  

## What

Reorder so the completion event is emitted and staged BEFORE the `git commit`, not after. 

**Current (broken, line 84):**
```bash
git commit → emit_event → tree dirty for next tick
```

**Fixed:**
```bash
emit_event "session_reflected" "autocommit: committing Tier-A on current branch"
git -C "$SUP" add events/ 2>/dev/null || true
# ... then git commit as before ...
# After commit, log the SHA but do NOT emit another event:
NEW_SHA=$(git -C "$SUP" rev-parse HEAD)
log "committed Tier-A writes on current branch and marked $BRANCH (sha=${NEW_SHA:0:12})"
```

## Why

Self-referential automation pollution — an automation step that records its own completion invalidates the precondition for the next automation step:

1. Autocommit fires, commits everything including `events/`
2. Post-commit, `emit_event` writes to `events/supervisor-events.jsonl`
3. Tree is now dirty (events/ modified after commit)
4. Tick fires 26 min later, finds dirty tree, skips
5. Next autocommit fires 2h later, commits the dirty event, emits another — loop repeats

**Impact:** verified-state.md is now **93h stale** (was 81h at C95). The tick has not run successfully. Automated dispatch cannot fire. Every 12h without the fix: +1 tick skip, +12h verified-state staleness, +12h governance drift.

## Verification before action

- [ ] Run `git log -5 --oneline supervisor/scripts/lib/supervisor-autocommit.sh` and check if this reorder is already in place
- [ ] Read `supervisor/scripts/lib/supervisor-autocommit.sh` lines 79-84 and verify current event emission order is `emit_event` AFTER `git commit`
- [ ] Confirm the tree is currently dirty due to this loop (check `git status` in supervisor repo for pending `events/` changes)

## Acceptance criteria

- [ ] The reorder specified above is applied to `supervisor/scripts/lib/supervisor-autocommit.sh:79-84`
- [ ] Change committed with message: "Fix autocommit event order: emit completion event before commit, not after (synthesis C96, P1)"
- [ ] No adversarial review required (mechanical reorder, low risk, verified unfixed this cycle)
- [ ] Completion report at `runtime/.handoff/general-supervisor-synthesis-p-autocommit-event-order-complete-<iso>.md` pointing back to this handoff

## Escalation

**URGENT if:**
- Primary verification reveals the proposal is already landed. Write completion report: "Already landed at commit <SHA>" and close.
- Tree is not currently dirty (the dirty tree is evidence the bug is active). If clean, investigate whether a different fix has already addressed it.
- The reorder conflicts with other pending changes in supervisor-autocommit.sh. Escalate with specific line conflict.

## Remarks

**This is the 4th synthesis cycle at priority #1.** It has passed the >3-cycle flag threshold. The fix is 3 lines. <10 min. Zero credentials. Zero risk. This is the single highest-leverage action in the workspace.
