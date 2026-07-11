---
from: synthesis-translator
to: general
date: 2026-06-05T03:29:57Z
priority: high
task_id: synthesis-events-autocommit
source_synthesis: /opt/workspace/runtime/.meta/cross-cutting-2026-06-05T03-26-55Z.md
source_proposal: P2 — Add `events/` to autocommit scope (19 cycles open)
---

# P2 — Add `events/` to autocommit scope

## Proposal body (from synthesis)

**Type:** Shared primitive update — `supervisor-autocommit.sh`.

**Blast radius:** Supervisor only (automatic). Combined with P1, permanently resolves the dirty-tree halt.

## Context

The synthesis file (cross-cutting-2026-06-05T03-26-55Z.md) lists the current dirty-tree state:
```
 M events/supervisor-events.jsonl
?? scripts/lib/.erofs-test-meta-reflection
?? scripts/lib/TEST_WRITE_2951547
```

The autocommit script currently covers only Tier-A governance paths (friction/, handoffs/, system/, ideas/, decisions/) but excludes events/. This means `supervisor-events.jsonl` remains dirty indefinitely, blocking the tick's dirty-tree gate.

This is part of a **19-cycle carry-forward** (since C60). The entire automated governance stack has been halted for ~336h (14 days) by the dirty-tree state.

## Verification before action (required)

- Read `supervisor/scripts/lib/supervisor-autocommit.sh` lines 54-57 (the Tier-A dirty check).
- Verify that `events/` is NOT currently listed in the `status --porcelain -- <paths>` check.
- If events/ is already included, write a completion report stating "already present" and close.
- Check git log to see if this has landed in a recent commit: `git log --oneline -10 supervisor/scripts/lib/supervisor-autocommit.sh`.

## Acceptance criteria

- Line 55-56 of `supervisor-autocommit.sh` is amended to include `events/` in the dirty-state check:
  ```bash
  TIER_A_DIRTY=$(git -C "$SUP" status --porcelain \
    -- friction/ handoffs/ system/ ideas/ decisions/ events/ 2>/dev/null || true)
  ```
- Alternative: if events/ should be excluded from autocommit (e.g. to preserve event ordering), explicitly document why in a comment and do not apply this change.
- Change committed with clear message: "Include events/ in autocommit scope to resolve dirty-tree blocker."
- Adversarial review optional (1-word addition, no logic change).
- Completion report at `runtime/.handoff/general-events-autocommit-complete-<iso>.md` pointing to commit SHA and this handoff.

## Escalation

URGENT if:
- The proposal contradicts a previous decision about event-file handling or autocommit scope (check `decisions/` before applying).
- The change would cause event-ordering issues or data loss (verify with Evan if uncertain).

---

**Note on P1:** This proposal is paired with P1 (remove test artifacts). P1 requires principal authorization. Once both are applied, the dirty-tree halt is resolved and the automated governance stack can resume. The synthesis notes: "P1 remains the critical unblock. It cascades to: tick resumption → verified-state refresh → INBOX processing → project tick dispatch → synthesis-to-execution conversion."
