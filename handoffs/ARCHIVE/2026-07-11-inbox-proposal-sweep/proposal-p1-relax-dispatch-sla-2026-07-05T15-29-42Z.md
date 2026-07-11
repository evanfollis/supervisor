---
from: synthesis-translator
to: executive
date: 2026-07-05T15:29:42Z
priority: high
task_id: synthesis-p1-relax-dispatch-sla
source_synthesis: /opt/workspace/runtime/.meta/cross-cutting-2026-07-05T15-26-01Z.md
source_proposal: "P1 (CARRY — C114, 13th cycle): Relax dispatch SLA 24h → 7d"
---

# P1: Relax dispatch SLA 24h → 7d

**Type:** CLAUDE.md amendment — "Automated Self-Reflection Loop" section.
**Blast radius:** Supervisor only. Automatic once CLAUDE.md is amended.

## Proposed change

In `/opt/workspace/CLAUDE.md`, find the "Dispatch obligation" section under "Automated Self-Reflection Loop". Current text:

```
**Dispatch obligation.** When a synthesis proposal lands in `runtime/.meta/cross-cutting-*.md`, the executive must dispatch a delegated project session within 24h
```

Amend to:

```
**Dispatch obligation.** When a synthesis proposal lands in `runtime/.meta/cross-cutting-*.md`, the executive must dispatch a delegated project session within 7 days
```

Update all references from "24h" to "7 days" in that section's text. The rule currently creates dispatch urgency that conflicts with synthesis counter-update format; increasing the SLA allows the reflection loop to be less noisy.

## Verification before action (required)

- Run `grep -n "dispatch" /opt/workspace/CLAUDE.md` to locate the current section
- Confirm the dispatch SLA still reads "24h" (not already updated)
- If already updated, write a completion report stating "already landed" rather than re-applying

## Acceptance criteria

- The text "within 24h" is replaced with "within 7 days" (or "7d" equivalent)
- The change committed with clear message: `amend dispatch SLA 24h → 7d per synthesis proposal P1`
- Completion report at `runtime/.handoff/general-p1-relax-dispatch-sla-complete-<iso>.md` pointing back to this handoff

## Escalation

URGENT if:
- The principal has explicitly stated the 24h SLA should remain unchanged (check JSONL).
- The change conflicts with another active decision in `supervisor/decisions/`.

---

**Background from synthesis (C126, unattended 26+ cycles):** The 24h SLA drives synthesis cycle cadence into 12h windows that require re-escalation for every standing recommendation that doesn't land. Increasing to 7d reduces noise while maintaining accountability. This is a P5-level fix (5 min patch).
