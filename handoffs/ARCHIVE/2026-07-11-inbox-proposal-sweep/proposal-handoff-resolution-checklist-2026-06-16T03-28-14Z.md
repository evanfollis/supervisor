---
from: synthesis-translator
to: general
date: 2026-06-16T03:28:14Z
priority: high
task_id: synthesis-handoff-resolution-checklist
source_synthesis: /opt/workspace/runtime/.meta/cross-cutting-2026-06-16T03-23-07Z.md
source_proposal: 5. P-handoff-resolution-checklist (carry from C93 — 9th cycle, PAST >3-CYCLE FLAG)
---

# P-handoff-resolution-checklist

**Type:** CLAUDE.md amendment.
**File:** `/opt/workspace/CLAUDE.md`
**Section:** "Session Awareness", after "After reading and acting on a handoff, delete the file."

**Proposed text:**
```markdown
- **When resolving an issue that has a corresponding handoff or URGENT
  file, delete the handoff file in the same session.** Do not defer
  cleanup to a future session. The resolving session has the context to
  confirm the issue is closed; a future session must re-derive that
  context from scratch, which consistently fails to happen.
```

**Blast radius:** All projects. Behavioral guidance. Low risk.

## Background

This proposal has been carried for 9 cycles. It addresses a behavioral pattern where resolved issues leave stale handoff files in place indefinitely, creating persistent false-positive escalations. By requiring the resolving session to clean up immediately, the queue reflects actual open issues, not historical noise.

The synthesis notes that runtime/.handoff/ and supervisor/handoffs/INBOX/ remain write-only surfaces with items as old as 43 days and 39 days respectively, creating a degraded escalation signal.

## Verification before action (required)

- Read `/opt/workspace/CLAUDE.md` section "Session Awareness". Check if guidance about deleting handoff files upon resolution already exists.
- Check for similar text in the "After reading and acting on a handoff" section that already covers this principle.
- If either check shows this guidance is already in place, write a completion report stating "already present in CLAUDE.md" rather than re-applying.

## Acceptance criteria

- Text added to `/opt/workspace/CLAUDE.md` in the "Session Awareness" section with clear guidance that resolving sessions must delete corresponding handoff files immediately.
- Guidance emphasizes same-session cleanup to prevent context loss.
- Change committed with a message explaining the motivation (prevent stale handoffs from degrading escalation signal).
- Completion report at `supervisor/handoffs/ARCHIVE/<iso>/general-handoff-resolution-checklist-complete.md` pointing back to this handoff and the source synthesis.

## Escalation

URGENT if:
- Verification reveals the guidance is already in place. Write a brief completion report and close.
- The Session Awareness section has structural changes that conflict with placement. Detail where the guidance should be added instead.
