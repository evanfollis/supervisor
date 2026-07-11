---
from: synthesis-translator
to: general
date: 2026-05-13T03:31:49Z
priority: medium
task_id: synthesis-carry-forward-acknowledgment-rule
source_synthesis: /opt/workspace/runtime/.meta/cross-cutting-2026-05-13T03-25-55Z.md
source_proposal: Proposal 4 — Synthesis carry-forward acknowledgment rule
---

# Synthesis carry-forward acknowledgment rule

## Summary

Proposals P1 (tick emission gate), P2 (reflect.sh Write bypass), and P3 (CURRENT_STATE.md auto-commit) have been in the top three of the cross-cutting synthesis for **5 consecutive cycles** (29–33). They are correctly formatted as dispatches and unconsumed, but the synthesis is re-proposing them every cycle, re-stating evidence without adding new information.

This proposal prevents the synthesis document from growing monotonically and ensures new findings get proportional attention by moving 5+-cycle carry-forwards to a "Standing" section rather than re-proposing them as top proposals.

## Proposed change

Target file: `/opt/workspace/supervisor/scripts/lib/synthesize-prompt.md`

Add a new section to the synthesis prompt:

```markdown
## Standing proposals (5+ cycles without resolution)

If a prior synthesis proposal has been in the top 3 for 5+ consecutive
cycles: move it here with a one-line status. Do not re-cite evidence.
Do not re-rank it. Name the blocker. Use the freed proposal slot for
new findings only.

Example entry:
- **Tick emission gate** — dispatched `general-tick-event-emission-gate-2026-05-12T04-49Z.md`; 5 cycles unconsumed. Blocker: attended-session time.
```

## Rationale (from synthesis)

The synthesis has produced the same top-3 proposals at a rate of 2/day. The cycle-32 synthesis repeated these exact proposals; this (cycle-33) synthesis has repeated them again. This accounts for:
- 10 synthesis cycles × 3 top-proposals = 30 proposal-slots consumed by the same 3 items
- Synthesis document growth as it re-cites evidence for identical proposals each cycle
- Competition for attention: new findings must fight for space in a document dominated by re-statements

Moving 5+-cycle carry-forwards to a "Standing" section is not an admission that the proposals are wrong. All three are valid, small-scope, high-leverage changes. The move is an acknowledgment that **synthesis can only re-state; it cannot execute**. The real problem is attention allocation in the attended-session layer, not synthesis quality.

## Implementation (notes)

- No changes to existing proposals; only *future* synthesis documents apply the rule.
- Standing proposals remain actionable — they are not archived or removed. The attended session can still consume them from the Standing section.
- If a standing proposal is resolved or explicitly deferred, it should be removed from Standing and moved to the resolution log.

## Verification before action (required)

- Verify `/opt/workspace/supervisor/scripts/lib/synthesize-prompt.md` exists and is readable.
- Check recent synthesis documents (cycles 32–33) to ensure the "Standing proposals" section does not already exist.
- If it exists, write a completion report stating "already in synthesize-prompt.md" rather than re-applying.

## Acceptance criteria

- The "Standing proposals" section (exact text or equivalent, including the example entry) is added to `/opt/workspace/supervisor/scripts/lib/synthesize-prompt.md`.
- The section is placed logically near the proposal-ranking guidance (typically after the "rank by impact" section).
- Change committed with clear message explaining the synthesis source and rationale.
- Completion report at `/opt/workspace/runtime/.handoff/general-general-synthesis-carry-forward-rule-complete-<iso>.md` pointing back to this handoff and the source synthesis.

## Escalation

URGENT if:
- The synthesize-prompt.md file has been restructured and the proposed section cannot fit logically. Report the new structure and ask for clarification on where to place the rule.
- A decision in `/opt/workspace/supervisor/decisions/` contradicts the carry-forward acknowledgment approach. Surface the conflict.
