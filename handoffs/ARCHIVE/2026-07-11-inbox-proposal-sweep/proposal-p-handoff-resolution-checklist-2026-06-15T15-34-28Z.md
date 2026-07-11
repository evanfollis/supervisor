---
from: synthesis-translator
to: general
date: 2026-06-15T15:34:28Z
priority: high
task_id: synthesis-p-handoff-resolution-checklist
source_synthesis: /opt/workspace/runtime/.meta/cross-cutting-2026-06-15T15-26-25Z.md
source_proposal: "Proposal 5 — P-handoff-resolution-checklist (carry from C93 — 8th cycle, PAST >3-CYCLE FLAG)"
---

# P-handoff-resolution-checklist

**Type:** CLAUDE.md amendment.
**File:** `/opt/workspace/CLAUDE.md`
**Section:** "Session Awareness", after "After reading and acting on a handoff, delete the file."

## Problem

Resolved issues accumulate stale handoff and URGENT files because the resolving session doesn't delete them. The next session must re-derive whether the issue is closed, which consistently fails to happen. This inflates the escalation surfaces and masks new signals.

## Solution

Add explicit guidance requiring the resolving session to delete the handoff file in the same session.

Add this text to `/opt/workspace/CLAUDE.md` under "Session Awareness" section, after the existing handoff-cleanup guidance:

```markdown
- **When resolving an issue that has a corresponding handoff or URGENT
  file, delete the handoff file in the same session.** Do not defer
  cleanup to a future session. The resolving session has the context to
  confirm the issue is closed; a future session must re-derive that
  context from scratch, which consistently fails to happen.
```

## Verification before action (required)

- Read `/opt/workspace/CLAUDE.md` and search for the "Session Awareness" section.
- Check if a similar handoff-deletion rule already exists in that section.
- If the exact guidance is already present, write a completion report stating "already landed" rather than re-applying.

## Acceptance criteria

- The proposed text is added to the "Session Awareness" section in `/opt/workspace/CLAUDE.md`.
- The guidance is placed after the existing "After reading and acting on a handoff, delete the file" line.
- Change committed with clear message: "Require handoff deletion on resolution, same session (synthesis C100, Proposal 5)".

## Escalation

URGENT if:
- Primary verification shows equivalent guidance is already in place. Write completion report stating "already landed" and close.
- The placement creates a conflict or redundancy with other handoff guidance. Escalate with the conflict named.

---

## Notes from synthesis

- Carried from C93 (8th cycle) — past the >3-cycle flag.
- Behavioral guidance, zero risk.
- Affects all projects via charter guidance.
- Directly addresses escalation-surface inflation (Pattern 2).
