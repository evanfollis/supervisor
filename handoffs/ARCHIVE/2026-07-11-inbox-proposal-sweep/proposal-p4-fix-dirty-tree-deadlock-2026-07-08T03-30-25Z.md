---
from: synthesis-translator
to: general
date: 2026-07-08T03:30:25Z
priority: urgent
task_id: synthesis-p4-dirty-tree-deadlock
source_synthesis: /opt/workspace/runtime/.meta/cross-cutting-2026-07-08T03-24-41Z.md
source_proposal: P4 — Fix dirty-tree deadlock
---

# P4: Fix dirty-tree deadlock

**Type:** `git -C /opt/workspace/supervisor pull --rebase` (5 seconds), then patch `supervisor-autocommit.sh:79-84` to detect 2-behind state and stage events continuously.

**Rationale:** Supervisor is now 561 ahead, 2 behind origin/main. The tick (primary autonomous actuator) has been blocked for 50 consecutive skip events. This is the single highest-leverage 5-second command in the workspace. All 561 ahead-commits are non-conflicting autocommit/reflection updates; the 2 behind-commits are similarly mechanical — the rebase will be clean.

**Blast radius:** Supervisor only. Unblocks the tick (primary autonomous actuator). Enables resolution of 11 of 25 standing recommendations.

---

## Verification before action (required)

**CRITICAL:** Before proceeding, run these checks locally:

```bash
cd /opt/workspace/supervisor
git status
git log --oneline origin/main..HEAD | head -10
git log --oneline HEAD..origin/main | head -10
```

Confirm:
- You see 561 ahead, 2 behind (or close)
- Ahead commits are autocommit-only (subject lines matching `autocommit YYYY-MM-DDTHH-MM-SSZ`)
- Behind commits are non-conflicting (2 mechanical commits)
- Working tree is clean (no untracked or staged changes)

If state differs materially, escalate instead of proceeding.

## Acceptance criteria

### Step 1: Rebase
```bash
cd /opt/workspace/supervisor
git pull --rebase origin main
```

Expected outcome:
- Rebase completes cleanly (no conflicts)
- `git log --oneline origin/main..HEAD` shows 0 (now at origin/main)
- `git status` shows "Your branch is ahead of 'origin/main' by <count> autocommit" (typical)

### Step 2: Patch supervisor-autocommit.sh

Edit `/opt/workspace/supervisor/scripts/lib/supervisor-autocommit.sh` lines 79-84.

Current code (check):
```bash
BRANCH="autocommit/$(date -u +%Y-%m-%d-%H)"

git -C "$SUP" \
  -c user.email='autocommit@workspace.local' \
  -c user.name='supervisor-autocommit' \
  commit --quiet -m "autocommit ${ISO_NOW}: Tier-A governance artifacts
```

After patching, detect 2-behind state. Add check after rebase:
```bash
BEHIND_COUNT=$(git -C "$SUP" log --oneline HEAD..origin/main 2>/dev/null | wc -l)
if (( BEHIND_COUNT > 0 )); then
  # 2-behind state detected; stage events continuously until caught up
  # (implementation: depends on specific autocommit.sh design; may involve loop or flag)
  log "2-behind state detected ($BEHIND_COUNT commits); staging events for next cycle"
fi
```

(The exact implementation depends on the intended behavior; the key is to handle the 2-behind case explicitly.)

### Step 3: Commit
- Commit the rebase and patch:
  ```bash
  git -C /opt/workspace/supervisor add supervisor/scripts/lib/supervisor-autocommit.sh
  git -C /opt/workspace/supervisor commit -m "Fix supervisor branch divergence and add 2-behind detection (synthesis-p4)"
  ```

### Step 4: Verification
- Run `workspace.sh context` to refresh state.
- Confirm supervisor ahead/behind count normalizes.
- Confirm the tick begins firing (check `supervisor/events/supervisor-events.jsonl` for new events or run `supervisor-tick.sh` manually if not scheduled).

## Non-goals

- Do not force-push.
- Do not discard the 2 behind-commits (let rebase handle them cleanly).
- Do not modify other scripts or governance files.

## Escalation

**URGENT if:**
- Rebase encounters conflicts → escalate with conflict details
- git pull fails with permission or auth error → surface the exact error
- State differs materially from 561/2 → escalate with actual state observed

## Completion report

Write to `/opt/workspace/supervisor/handoffs/INBOX/general-synthesis-p4-deadlock-complete-<iso>.md`:
- Rebase outcome (clean/conflicted)
- Commit SHA of the patch
- Tick resumption verification (did it fire after the fix?)
- Any observations about standing recommendations that now unblock
