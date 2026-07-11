---
from: synthesis-translator
to: general
date: 2026-05-31T15:27:59Z
priority: high
task_id: synthesis-p2-dirty-tree-whitelist
source_synthesis: /opt/workspace/runtime/.meta/cross-cutting-2026-05-31T15-23-50Z.md
source_proposal: P2 — Dirty-tree whitelist for tick
---

# P2 — Dirty-tree whitelist for tick

**Type**: Shared primitive edit — `supervisor/scripts/lib/supervisor-tick.sh`

**Change**: The tick's dirty-tree check (currently at lines 150-156) should whitelist paths that autocommit handles (Tier-A: `friction/`, `handoffs/`, `system/`, `ideas/`, `decisions/`, `events/`) and paths that are expected to be modified by the tick itself (e.g., `events/supervisor-events.jsonl`).

Current problematic code (lines 150-156):
```bash
PRE_SUP_DIRTY=$(git -C "$SUP" status --porcelain -- . ':!system/verified-state.md' 2>/dev/null | grep -v '^??' || true)

# Refuse to run on a dirty working tree — an attended session may be in flight
# with uncommitted work. Safer to skip than to risk committing partial state.
if [[ -n "$PRE_SUP_DIRTY" ]]; then
  skip_with_reason "supervisor working tree was dirty at tick start; refusing to run"
fi
```

Should be updated to exclude Tier-A paths that autocommit will handle plus tick-expected outputs.

**Blast radius**: Supervisor only. Automatic.

**Rationale**: This prevents future halt recurrence from the same class. The tick has been blocked because event writes to `events/` make the supervisor dirty, but those writes are part of normal operation and should not block the tick. The dirty-tree gate was designed to catch unintended edits by attended sessions, not to block on files that autocommit is actively managing.

## Verification before action (required)

- Run `git log --oneline -5` on `supervisor/`. Check if this patch has already landed.
- Read `supervisor/scripts/lib/supervisor-tick.sh` lines 150-156. Verify the dirty-tree check does NOT yet whitelist Tier-A paths and tick outputs.
- If either check shows this is already applied, write a completion report stating "already landed" rather than re-applying.

## Acceptance criteria

- The dirty-tree check now excludes Tier-A governance paths (`friction/`, `handoffs/`, `system/`, `ideas/`, `decisions/`, `events/`) and tick-generated outputs.
- Change committed with clear message explaining the synthesis source and the rationale.
- Completion report at `runtime/.handoff/general-supervisor-synthesis-p2-complete-<iso>.md` pointing back to this handoff.

## Escalation

URGENT if:
- Primary verification reveals this patch has already landed. Write a brief completion report saying "already landed" and close.
- The change would require more extensive refactoring than the synthesis proposed. Escalate with the specific blockers.
