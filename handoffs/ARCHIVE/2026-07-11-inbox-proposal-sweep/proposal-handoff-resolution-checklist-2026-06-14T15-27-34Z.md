---
from: synthesis-translator
to: general
date: 2026-06-14T15:27:34Z
priority: medium
task_id: synthesis-handoff-resolution-checklist
source_synthesis: /opt/workspace/runtime/.meta/cross-cutting-2026-06-14T15-23-48Z.md
source_proposal: 5. P-handoff-resolution-checklist (carry from C93 — 6th cycle, PAST >3-CYCLE FLAG)
---

# P-handoff-resolution-checklist — Explicit handoff cleanup on resolution

## Proposal

Amend `/opt/workspace/CLAUDE.md` (workspace root instructions) in the "Session Awareness" section to add explicit guidance that when a session resolves an issue with a corresponding handoff or URGENT file, the handoff must be deleted in that same session.

This closes a behavioral loop: resolving sessions have the context to confirm an issue is closed; future sessions must re-derive that context from scratch, which consistently fails. Making cleanup mandatory prevents stale handoffs from accumulating.

## Full proposal text from synthesis

**Type:** CLAUDE.md amendment.
**Section:** "Session Awareness", after "After reading and acting on a
handoff, delete the file."

**Proposed text:**
```markdown
- **When resolving an issue that has a corresponding handoff or URGENT
  file, delete the handoff file in the same session.** Do not defer
  cleanup to a future session. The resolving session has the context to
  confirm the issue is closed; a future session must re-derive that
  context from scratch, which consistently fails to happen.
```

**Blast radius:** All projects. Behavioral guidance. Low risk.

## Verification before action (required)

- Read `/opt/workspace/CLAUDE.md` and locate the "Session Awareness" section.
- Verify the current guidance about handoff cleanup (look for "After reading and acting on a handoff, delete the file").
- Check whether similar guidance exists elsewhere in the document that might be redundant or need updating.

## Acceptance criteria

- The new guideline is added to `/opt/workspace/CLAUDE.md` in the "Session Awareness" section.
- It appears immediately after or near the existing "After reading and acting on a handoff, delete the file" guidance.
- The text makes clear that deletion is mandatory in the resolving session, not deferred.
- Commit message cites the synthesis analysis (stale handoffs accumulate because cleanup is deferred).
- No other changes to CLAUDE.md in this commit.

## Escalation

URGENT if:
- The "Session Awareness" section structure has changed significantly. Describe the current structure and propose a location for the new guidance.
- Conflicting guidance exists in CLAUDE.md that contradicts this rule (e.g., "defer cleanup for audit trail"). If so, surface the conflict for principal decision.
