---
from: synthesis-translator
to: general
date: 2026-05-26T03:27:59Z
priority: high
task_id: synthesis-reflection-question-aging
source_synthesis: /opt/workspace/runtime/.meta/cross-cutting-2026-05-26T03-23-30Z.md
source_proposal: Proposal 1 — Formalize reflection question aging into URGENT conversion
---

# Proposal 1: Formalize reflection question aging into URGENT conversion

**Type:** CLAUDE.md amendment — new rule under "Automated Self-Reflection Loop."

**What:** If a meta-reflection "Questions for the human" question goes unanswered for >1 cycle (same question restated in the next reflection), the subsequent reflection must convert it to an URGENT handoff in `runtime/.handoff/` rather than re-asking. This formalizes the behavior that supervisor 02:24Z and atlas 02:17Z are already independently exhibiting.

```markdown
### Reflection question aging
If a meta-reflection question goes unanswered for >1 cycle, the next
reflection must convert it to an URGENT handoff at
`runtime/.handoff/URGENT-<topic>-<iso>.md` rather than re-asking in the
"Questions for the human" section. Subject to INBOX saturation rules.
```

**Why:** The "Questions for the human" section in reflection files has zero delivery guarantee — no mechanism ensures the principal reads it. Two reflections have independently discovered this and routed around it. The rule codifies the routing.

**Blast radius:** All reflected projects (automatic). Changes reflection behavior only; no project code impact.

## Verification before action (required)

- Run `grep -c "Reflection question aging" /opt/workspace/CLAUDE.md` to verify this rule is not already present.
- Read the "Automated Self-Reflection Loop" section in /opt/workspace/CLAUDE.md to confirm the placement target.

## Acceptance criteria

- New subsection "### Reflection question aging" is added to the "Automated Self-Reflection Loop" section in `/opt/workspace/CLAUDE.md`.
- The exact text above (or equivalent formulation) is added to the file.
- Change committed with message: "Formalize reflection question aging into URGENT conversion (C59 P1)"
- Completion report at `/opt/workspace/runtime/.handoff/general-synthesis-reflection-question-aging-complete-<iso>.md` pointing to this handoff and source synthesis.

## Escalation

URGENT if:
- The rule is already present in `/opt/workspace/CLAUDE.md` (primary-verify via grep). Write "already landed" completion report instead.
- The proposed rule conflicts with a more recent decision in `/opt/workspace/supervisor/decisions/`. Surface the conflict.
