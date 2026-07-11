---
from: synthesis-translator
to: general
date: 2026-06-15T03:30:46Z
priority: medium
task_id: synthesis-p-handoff-resolution-checklist
source_synthesis: /opt/workspace/runtime/.meta/cross-cutting-2026-06-15T03-27-01Z.md
source_proposal: Proposal 5 — P-handoff-resolution-checklist
---

# P-handoff-resolution-checklist (carry from C93 — 7th cycle, PAST >3-CYCLE FLAG)

**Type:** CLAUDE.md amendment.
**File:** `/opt/workspace/CLAUDE.md`

## What

Add a resolution-checklist item to the "Session Awareness" section to enforce immediate cleanup of handoffs when issues are resolved. This prevents resolved items from accumulating in the queue and becoming stale reference artifacts.

## Proposed text amendment to /opt/workspace/CLAUDE.md

In the **Session Awareness** section, after the existing line "- After reading and acting on a handoff, delete the file.", add:

```markdown
- **When resolving an issue that has a corresponding handoff or URGENT
  file, delete the handoff file in the same session.** Do not defer
  cleanup to a future session. The resolving session has the context to
  confirm the issue is closed; a future session must re-derive that
  context from scratch, which consistently fails to happen.
```

## Blast radius

All projects. Behavioral guidance. Low risk.

## Verification before action (required)

- Check that this exact text does not already exist in /opt/workspace/CLAUDE.md
- Verify the location in "Session Awareness" section is appropriate

## Acceptance criteria

- The proposed text is added to /opt/workspace/CLAUDE.md under "Session Awareness"
- Change committed with clear message referencing the synthesis source (cleanup discipline)
- Completion report at `runtime/.handoff/general-synthesis-p-handoff-resolution-checklist-complete-<iso>.md`

## Escalation

URGENT if:
- The text already exists in CLAUDE.md (verify and close)
- The wording conflicts with other guidance in the session-awareness section
