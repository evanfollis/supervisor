---
from: synthesis-translator
to: general
date: 2026-05-13T03:31:49Z
priority: high
task_id: synthesis-infrastructure-handoff-priority-signal
source_synthesis: /opt/workspace/runtime/.meta/cross-cutting-2026-05-13T03-25-55Z.md
source_proposal: Proposal 2 — Infrastructure handoff priority signal
---

# Infrastructure handoff priority signal

## Summary

The empirical finding: 4-for-4 product-visible handoffs consumed within hours; 0-for-7 infrastructure handoffs unconsumed over 12–287h, same directory, same format. The attended session's implicit priority is "product first," which is correct for normal operation but incorrect when infrastructure repair has been waiting 5+ synthesis cycles.

This proposal adds an explicit ordering constraint to the executive reentry procedure to prioritize infrastructure-repair work older than 24h.

## Proposed CLAUDE.md amendment

Target file: `/opt/workspace/CLAUDE.md` § Session Awareness

Add a new sub-bullet under the handoff-list step:

```
**Infrastructure-repair handoffs (names matching `general-reflect-sh-*`,
`general-tick-*`, `URGENT-general-adversarial-*`) must be processed
before product-visible handoffs when they have been unconsumed for
>24h.** The executive session's reentry procedure already lists
`runtime/.handoff/general-*`; this adds an ordering constraint:
infrastructure items older than 24h sort to the top. Rationale:
infrastructure repair affects all projects; product-visible fixes
affect one. Deferring infrastructure to process product work is a
local optimization that degrades the workspace-wide feedback loop.
```

## Rationale (from synthesis)

The dispatch-via-handoff pathway is now 4-for-4 for product-visible work (sourceType → deploy gate → symphony eviction → latest fix all within hours). But the infrastructure repair handoffs from the same period remain unconsumed at 12–287h ages. The reflection loop faithfully diagnoses these, but the attended session does not reach them.

This is not a mechanism problem — the handoff format is working. It is an attention allocation problem. This amendment makes the priority constraint explicit rather than implicit.

## Verification before action (required)

- Run `git log --oneline -20` on supervisor. Check if this amendment has landed via another path.
- Read `/opt/workspace/CLAUDE.md` § Session Awareness. Verify the text is not already present.
- If either is true, write a completion report stating "already landed at commit <SHA> / verified in-file" rather than re-applying.

## Acceptance criteria

- The amendment (exact text above) is inserted into `/opt/workspace/CLAUDE.md` § Session Awareness.
- Change committed with clear message explaining the synthesis source and rationale.
- Completion report at `/opt/workspace/runtime/.handoff/general-general-infrastructure-handoff-priority-complete-<iso>.md` pointing back to this handoff and the source synthesis.

## Escalation

URGENT if:
- The amendment conflicts with a more recent decision in `/opt/workspace/supervisor/decisions/`. Do not force-apply; surface the conflict.
- `/opt/workspace/CLAUDE.md` § Session Awareness structure differs from what the proposal assumes (e.g., section renamed or removed). Report the mismatch and ask for clarification on where to place the text.
