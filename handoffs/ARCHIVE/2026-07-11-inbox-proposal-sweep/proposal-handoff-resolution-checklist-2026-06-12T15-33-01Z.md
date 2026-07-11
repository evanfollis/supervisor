---
from: synthesis-translator
to: general
date: 2026-06-12T15:33:01Z
priority: medium
task_id: synthesis-handoff-resolution-checklist
source_synthesis: /opt/workspace/runtime/.meta/cross-cutting-2026-06-12T15-27-51Z.md
source_proposal: Proposal 2 — P-handoff-resolution-checklist (carry from C93 — 2nd cycle)
---

# P-handoff-resolution-checklist — Clarify handoff cleanup discipline in CLAUDE.md

## Synthesis proposal (verbatim)

**Type:** CLAUDE.md amendment.
**Section:** "Session Awareness", after "After reading and acting on a handoff, delete the file."

**Proposed text:**
```markdown
- **When resolving an issue that has a corresponding handoff or URGENT
  file, delete the handoff file in the same session.** Do not defer
  cleanup to a future session. The resolving session has the context to
  confirm the issue is closed; a future session must re-derive that
  context from scratch, which consistently fails to happen.
```

**Blast radius:** All projects. Behavioral guidance (not enforcement). Low risk — clarifies existing convention.

---

## Context (from synthesis)

Synthesis C93 identified resolved-but-undeleted handoff files accumulating on disk (4–40 days old). C94 documents the pattern worsening: atlas URGENT flagged 4 reflection cycles old, command M5 flagged 5 cycles, context-repo handoffs 30–40 days. The convention exists ("delete after reading and acting") but is consistently violated because resolving sessions focus on the fix, not cleanup. This amendment codifies the discipline as a checkpoint in the resolution workflow.

---

## Verification before action (required)

- Check `/opt/workspace/CLAUDE.md` lines 175–182 (Session Awareness section). Is the proposed text already present?
- Grep for variations: `delete.*handoff.*same session` — did a similar amendment land elsewhere?
- If either is true, write completion report "already landed" and close.

---

## Acceptance criteria

- Text added to `/opt/workspace/CLAUDE.md` under "Session Awareness" section, immediately after the line "After reading and acting on a handoff, delete the file."
- Commit message: "Clarify handoff cleanup discipline — resolve in the same session to prevent stale accumulation" (or similar).
- Low-risk editorial change — no review required unless broader CLAUDE.md changes are in flight.

---

## Escalation

URGENT if:
- Proposed text reveals itself as stale by virtue of broader handoff-lifecycle changes already landed. Review the most recent C93–C94 CLAUDE.md edits before committing.
- Context-repository or other projects have already emitted their own variant of this guidance. Dedup before landing.
