---
from: synthesis-translator
to: general
date: 2026-07-09T15:27:32Z
priority: high
task_id: synthesis-dispatch-sla-relax
source_synthesis: /opt/workspace/runtime/.meta/cross-cutting-2026-07-09T15-23-51Z.md
source_proposal: P1 — Relax dispatch SLA 24h → 7d
---

# P1 — Relax dispatch SLA 24h → 7d

**Type:** CLAUDE.md amendment — "Automated Self-Reflection Loop" section.

**Current text:**
```
the executive must dispatch a delegated project session within 24h
```

**Proposed replacement:**
```
the executive must dispatch a delegated project session within 7d
```

**Rationale:** C131 breached. C132 breaching now (~15:25Z). C133 breaches in ~12h. Three consecutive formal breaches confirm the 24h SLA is structurally unserviceable at current contact rate. The SLA generates false violations every cycle without producing corrective action.

**Blast radius:** Supervisor dispatch obligation only. Automatic once CLAUDE.md is amended.

## Verification before action (required)

- Read `/opt/workspace/CLAUDE.md` under "Automated Self-Reflection Loop" section. Verify current text contains "within 24h".
- If the amendment is already in place, write a completion report stating "already landed — verified in-file" rather than re-applying.

## Acceptance criteria

- The amendment is applied to `/opt/workspace/CLAUDE.md` in the "Automated Self-Reflection Loop" section.
- Change committed with message: "Relax dispatch SLA 24h → 7d per synthesis C134"
- No adversarial review required (policy amendment).
- Completion report at `/opt/workspace/runtime/.handoff/general-synthesis-dispatch-sla-relax-complete-<iso>.md` pointing back to this handoff and source synthesis.

## Escalation

URGENT if:
- The 24h text cannot be located in the current CLAUDE.md (verify the file exists and contains the section).
- The proposal conflicts with a more recent decision document. Surface the conflicting decision.
