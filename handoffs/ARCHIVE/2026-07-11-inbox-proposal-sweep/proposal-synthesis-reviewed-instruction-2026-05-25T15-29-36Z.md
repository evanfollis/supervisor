---
from: synthesis-translator
to: general
date: 2026-05-25T15:29:36Z
priority: high
task_id: synthesis-reviewed-prompt-fix
source_synthesis: /opt/workspace/runtime/.meta/cross-cutting-2026-05-25T15-25-05Z.md
source_proposal: Proposal 3 (CARRY-FORWARD from C57): Add explicit `synthesis_reviewed` instruction to tick prompt
---

# Add explicit `synthesis_reviewed` instruction to tick prompt

## Proposal body

**Type:** Shared primitive fix (`supervisor-tick-prompt.md`).

**What:** Add explicit emit instruction after synthesis consumption in step 6.

**Status:** 2nd synthesis cycle. The event was restored at 04:47Z by model inference, but the prompt template still has 0 mentions of `synthesis_reviewed`.

**Blocker classification:** **Attended-session-blocked.** One-line addition to the prompt template. No judgment or principal decision required.

**Blast radius:** Supervisor tick only (automatic).

**Why:** C57 Proposal 1 (make the instruction explicit) would make this durable. Without it, the restoration depends on model inference continuing to hold — the same mechanism that failed for cycles 55–56. Hardening the prompt template makes the event emission explicit and non-fragile.

## Verification before action (required)

- Check current state: `grep -c "synthesis_reviewed" /opt/workspace/supervisor/scripts/lib/supervisor-tick-prompt.md` — should return 0 if not yet landed.
- Read the supervisor-tick-prompt.md file and locate step 6 (synthesis consumption step).
- If `synthesis_reviewed` appears multiple times in the file, mark as already-landed and close.

## Acceptance criteria

- The supervisor-tick-prompt.md file includes an explicit instruction after step 6 (synthesis consumption) to emit a `synthesis_reviewed` event.
- The instruction should be clear and actionable (e.g., "After consuming synthesis, emit `synthesis_reviewed` event with the synthesis file path").
- Change committed with clear message referencing synthesis cycle 58.
- No adversarial review needed (prompt template amendment, no structural code change).

## Escalation

URGENT if `grep -c "synthesis_reviewed" /opt/workspace/supervisor/scripts/lib/supervisor-tick-prompt.md` returns a non-zero count — the proposal is already landed. Close with a note saying the instruction was added in an earlier cycle.

---

## Completion report template

After landing, write a completion report at:
`/opt/workspace/runtime/.handoff/general-synthesis-reviewed-instruction-complete-<iso>.md`

Include:
- Commit SHA where the change landed
- Brief note: "Explicit synthesis_reviewed instruction added to tick prompt per synthesis C58 proposal 3"
- Reference back to this handoff
