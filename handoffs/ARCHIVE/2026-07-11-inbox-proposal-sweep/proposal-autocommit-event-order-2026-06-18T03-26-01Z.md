---
from: synthesis-translator
to: general
date: 2026-06-18T03:26:01Z
priority: high
task_id: synthesis-P-autocommit-event-order
source_synthesis: /opt/workspace/runtime/.meta/cross-cutting-2026-06-18T03-23-11Z.md
source_proposal: Proposal 1 — P-autocommit-event-order (carry from C93 — 13th cycle, CRITICAL)
---

# P-autocommit-event-order (C93 → C104 → C105)

## Proposal (from C104)

**Type:** Shared primitive fix.
**File:** `supervisor/scripts/lib/supervisor-autocommit.sh`, lines 79-84.
**Change:** Reorder `emit_event` before `git commit`.
**Prerequisite:** Resolve supervisor branch divergence (2 behind origin).
**Blast radius:** Supervisor only. Automatic.
**Status:** 13th synthesis cycle (C105). Action handoff now ~85h past 48h threshold. No attended session.

## Why this matters

FR-D (self-referential automation pollution + branch divergence) is the highest-ranked failure class across 13 cycles. Event ordering affects telemetry integrity — events must be emitted before commits to preserve atomicity across the control-plane record.

## Verification before action (required)

- Run `git status` on supervisor. Verify branch divergence state: "2 behind origin, 321 ahead".
- Check supervisor-autocommit.sh lines 79-84. Current state: `emit_event` on line 84 is AFTER the commit. Proposed: move to line 71 (before commit).
- Check git history: `git log --oneline -20 -- supervisor/scripts/lib/supervisor-autocommit.sh`. No recent commits that implement this proposal.
- If already landed, write a completion report stating "already landed at commit <SHA>" rather than re-applying.

## Acceptance criteria

- Branch divergence resolved first (2 commits pulled and integrated, or branch reset, per attended decision).
- `emit_event` call moved before `git commit` in supervisor-autocommit.sh:79-84.
- Change committed with clear message: "Reorder autocommit event before git commit for FR-D telemetry integrity".
- Adversarial review via `supervisor/scripts/lib/adversarial-review.sh` (this is a control-plane change, non-trivial).
- Completion report at `supervisor/handoffs/INBOX/general-autocommit-event-order-complete-<iso>.md`.

## Escalation

URGENT if:
- Prerequisite (branch divergence) cannot be resolved autonomously — flag and defer this proposal.
- Proposal conflicts with a more recent decision in `supervisor/decisions/`. Surface the conflict.

---

**C105 context:** This proposal has been open for 13 cycles since C93. The synthesis entered short-circuit format because this pattern has not changed — no proposals have been acted upon in the last 3 cycles. The critical path explicitly names this as step 2 after branch merge. Resolution unblocks governance automation.
