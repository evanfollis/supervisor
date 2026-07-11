---
from: synthesis-translator
to: general
date: 2026-06-17T03:29:34Z
priority: high
task_id: synthesis-autocommit-event-order
source_synthesis: /opt/workspace/runtime/.meta/cross-cutting-2026-06-17T03-26-25Z.md
source_proposal: "Proposal 1: P-autocommit-event-order (carry from C93 — 11th cycle, CRITICAL)"
---

# P-autocommit-event-order — FR-D critical fix

**Type:** Shared primitive fix.
**File:** `supervisor/scripts/lib/supervisor-autocommit.sh`, lines 79-84.
**Change:** Reorder `emit_event` before `git commit`.
**Prerequisite:** Resolve supervisor branch divergence (2 behind origin).
**Blast radius:** Supervisor only. Automatic.
**Status:** 11th synthesis cycle. Action handoff at ~61h. No attended session.

## Full proposal

This is the FR-D (single point of failure) critical fix that has been carried forward for 11 consecutive synthesis cycles since C93. The synthesis notes:

> **Rank: 1 (unchanged since C93).**
> 
> Updated counters (delta from C102):
> - verified-state.md: **~178h stale** (was ~165.6h)
> - Supervisor remote: **309 commits ahead, 2 behind** (was 302+2)
> - Tick consecutive skips: 10+ per window, 11 consecutive windows
> - Dispatch obligation breaches: 11 consecutive
> - INBOX: 198+ items (stable — no new translator deposits observed)
> - FR-D action handoff: **~61h** (well past 48h threshold)
>
> Fix unchanged: 3 lines in `supervisor/scripts/lib/supervisor-autocommit.sh:79-84`.
> Prerequisite unchanged: resolve 2-behind branch divergence first.

**Failure class:** Self-referential automation pollution + branch divergence.

## Verification before action (required)

- Check `supervisor/scripts/lib/supervisor-autocommit.sh` lines 79-84. Verify the current order of operations: does `emit_event` happen before or after `git commit`? (Currently it happens after.)
- Check supervisor git status: `git -C /opt/workspace/supervisor log --oneline -5` to see recent commits. Look for evidence this fix has already landed.
- If already applied, write a completion report "already landed" and close this handoff.

## What needs to change

The current code order (lines 79-84):
```bash
git -C "$SUP" \
  -c user.email='autocommit@workspace.local' \
  -c user.name='supervisor-autocommit' \
  commit --quiet -m "autocommit ${ISO_NOW}: Tier-A governance artifacts
...
emit_event "session_reflected" "autocommit: committed Tier-A..."
```

Should become:
```bash
emit_event "session_reflected" "autocommit: about to commit Tier-A..."
git -C "$SUP" \
  -c user.email='autocommit@workspace.local' \
  -c user.name='supervisor-autocommit' \
  commit --quiet -m "autocommit ${ISO_NOW}: Tier-A governance artifacts
...
```

(Event emission moved before commit; message adjusted to reflect intent rather than completion.)

## Acceptance criteria

- The patch specified above is applied to `supervisor/scripts/lib/supervisor-autocommit.sh`.
- Change committed with message: "Fix telemetry event ordering in supervisor-autocommit (FR-D)"
- No adversarial review required for this mechanical reorder.
- Completion report at `runtime/.handoff/general-supervisor-synthesis-autocommit-event-order-complete-<iso>.md` pointing back to this handoff.

## Escalation

URGENT if:
- Prerequisite not met: supervisor branch is still 2 commits behind origin. Do not force-apply; emit URGENT to general noting the prerequisite blocker.
- Fix conflicts with more recent commit. Check git log before applying.

## Notes

This fix unblocks the critical path for supervisor automation recovery. It has been waiting 11 cycles for attended execution. Mark for rapid dispatch.
