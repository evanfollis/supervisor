---
from: synthesis-translator
to: executive
date: 2026-06-29T15:30:33Z
priority: critical
task_id: synthesis-p4-dirty-tree-deadlock
source_synthesis: /opt/workspace/runtime/.meta/cross-cutting-2026-06-29T15-27-11Z.md
source_proposal: P4 (CARRY) — Fix dirty-tree deadlock (P-autocommit-event-order)
---

# P4 (CARRY): Fix dirty-tree deadlock (P-autocommit-event-order)

**Status:** 28th carry-forward cycle. Supervisor branch is 2 commits behind origin/main. Requires the rebase first (`git pull --rebase` on supervisor). The rebase has been requested in **14 consecutive synthesis cycles** (C99–C114) without authorization or recorded deferral.

**Current state (verified 2026-06-29T15:30Z):**
```
supervisor: 2 behind origin/main, 459 ahead
autocommit exits with code 1 on dirty-tree gate deadlock
tick loop blocked by dirty-tree state
```

**What needs to happen:**

1. **Rebase supervisor to origin/main:**
   ```bash
   cd /opt/workspace/supervisor
   git pull --rebase origin main
   ```

2. **Fix autocommit event ordering** at `supervisor-autocommit.sh:79-84`:
   - Current code commits with agent="autocommit" but the commit happens BEFORE event emission.
   - Event emission (line 84) fires AFTER the commit, and references the commit SHA.
   - The event should be emitted BEFORE commit so the commit itself logs the event in its message or immediately after to preserve ordering.
   - This is the `P-autocommit-event-order` issue referenced in the synthesis.

3. **Push supervisor to origin/main:**
   ```bash
   cd /opt/workspace/supervisor
   git push origin main
   ```

**Impact:** Once this is done:
- Supervisor dirty-tree gate is unblocked
- Supervisor tick loop can resume
- Governance automation (dispatch obligations, INBOX management) can resume
- verified-state refresh can happen
- All standing recommendations depending on supervisor unblock can progress

**Blast radius:** Supervisor only. Unblocks: tick loop, verified-state refresh, dispatch obligation enforcement, governance automation.

## Verification before action (required)

- Run `git log --oneline -5` on `/opt/workspace/supervisor/` to see current state.
- Run `git rev-list --left-right --count origin/main...HEAD` to verify the "2 behind" state.
- Run `git status --short` to see current dirty state.
- Run `git log origin/main..HEAD --oneline | wc -l` to confirm the carry-forward state.
- If the rebase has already been done or the 2-behind state is resolved, write a completion report stating "already landed at commit <SHA>" rather than re-applying.

## Acceptance criteria

- Supervisor is rebased to origin/main (no "2 behind" state when running `git rev-list --left-right --count origin/main...HEAD`).
- Autocommit event ordering is fixed (verify in `supervisor-autocommit.sh` that event emission is properly ordered relative to commit).
- Changes are pushed to origin/main.
- Supervisor dirty-tree state is clean (verify with `git status --short`).
- Completion report at `runtime/.handoff/general-supervisor-synthesis-p4-complete-<iso>.md` pointing back to this handoff, the source synthesis, and the specific commits applied.

## Escalation

URGENT if:
- The rebase encounters merge conflicts. Do not force-resolve without understanding the conflict context.
- The autocommit event-order fix is unclear or requires additional investigation. Escalate with the specific ordering issue identified.
- A more recent decision in `supervisor/decisions/` blocks the rebase or event-order fix. Verify and escalate the conflict.
- Principal has recorded a deferral reason for the rebase in `supervisor/decisions/` or a JSONL user turn. Respect that and write a completion report explaining the deferral.
