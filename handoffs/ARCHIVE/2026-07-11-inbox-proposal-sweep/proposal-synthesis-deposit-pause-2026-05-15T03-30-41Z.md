---
from: synthesis-translator
to: general
date: 2026-05-15T03:30:41Z
priority: high
task_id: synthesis-synthesis-deposit-pause
source_synthesis: /opt/workspace/runtime/.meta/cross-cutting-2026-05-15T03-25-46Z.md
source_proposal: Proposal 2 (CARRIED from cycle 36, self-adopted this cycle)
---

# Synthesis deposit pause during INBOX saturation

**Cycle 36 Proposal 5.** This synthesis cycle adopts it: no new INBOX files were written despite actionable items in the proposals section. The rule should be codified in CLAUDE.md to bind future synthesis cycles and the tick dispatcher.

**Section:** Automated Self-Reflection Loop (append to existing INBOX saturation exception)

Add the following entry after the existing "INBOX saturation exception" bullet point:

> When INBOX holds >10 items and consumption rate has been 0 for 3+ consecutive synthesis cycles, the synthesis job writes proposals to `runtime/.meta/cross-cutting-*.md` only. The tick dispatcher does NOT create corresponding INBOX items until the backlog falls below 8.

**Blast radius:** Supervisor tick dispatcher + synthesis job (automatic). This prevents the queue from becoming a noise channel when executive consumption has stalled.

## Verification before action (required)

- Run `grep -n "When INBOX holds >10 items and consumption rate" /opt/workspace/CLAUDE.md`. If this returns a match, the proposal is already landed.
- Check the "Automated Self-Reflection Loop" section to confirm the insertion point is after the existing "INBOX saturation exception" bullet.
- If the text already exists, write a completion report stating "already landed" rather than re-applying.

## Acceptance criteria

- The amendment text (quoted above) is added to the "Automated Self-Reflection Loop" section, appended after the existing "INBOX saturation exception" bullet point.
- Change committed with clear message explaining the synthesis source (cycle 36 proposal, adopted in cycle 37).
- Completion report at `runtime/.handoff/general-general-synthesis-synthesis-deposit-pause-complete-<iso>.md` pointing back to this handoff and the source synthesis.

## Escalation

URGENT if:
- The deposit pause conflicts with other synthesis/dispatcher logic already in place (should be reconciled, not forced).
- Clarification needed on the exact condition for resuming deposits (drops below 8).
