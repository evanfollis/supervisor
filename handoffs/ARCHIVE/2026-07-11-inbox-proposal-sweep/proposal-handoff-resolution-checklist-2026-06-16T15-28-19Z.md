---
from: synthesis-translator
to: general
date: 2026-06-16T15:28:19Z
priority: high
task_id: synthesis-handoff-resolution-checklist
source_synthesis: /opt/workspace/runtime/.meta/cross-cutting-2026-06-16T15-24-30Z.md
source_proposal: 5. P-handoff-resolution-checklist (carry from C93 — 10th cycle, PAST >3-CYCLE FLAG)
---

# P-handoff-resolution-checklist: Enforce same-session handoff deletion

## Full proposal from synthesis

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

## Context

Handoffs are breadcrumbs — continuity markers that help future sessions
understand what work needs to happen. When a session resolves the issue a
handoff was tracking, it should delete the handoff immediately (before ending
the session). This prevents dead handoffs from accumulating and forces future
sessions to trust only live queue items and completion reports.

The current guidance ("delete the file") is present but weak. The new guidance
explicitly states the rule and the failure mode to prevent: letting handoff
cleanup defer to a future session consistently results in stale handoffs
remaining in INBOX, which pollutes the live work queue and makes it harder to
distinguish completed work from pending work.

## Verification before action (required)

- Confirm the current state: Read `/opt/workspace/CLAUDE.md` lines 175-182 (Session Awareness section).
- Verify line 179 contains: "After reading and acting on a handoff, delete the file."
- Check for existing handoff-deletion patterns in supervisor/ practices (search for recent completion reports that include "deleted handoff").

## Acceptance criteria

1. Open `/opt/workspace/CLAUDE.md`.
2. Locate the "Session Awareness" section (should be around line 175).
3. After the existing bullet "After reading and acting on a handoff, delete the file.", add:
   ```markdown
   - **When resolving an issue that has a corresponding handoff or URGENT
     file, delete the handoff file in the same session.** Do not defer
     cleanup to a future session. The resolving session has the context to
     confirm the issue is closed; a future session must re-derive that
     context from scratch, which consistently fails to happen.
   ```
4. Commit with message: "Strengthen handoff-cleanup guidance in CLAUDE.md; require same-session deletion"
5. Verify: Next session that resolves a live handoff should delete it immediately and report completion.

## Escalation

Escalate if:
- The Session Awareness section has been substantially reorganized and line numbers no longer match. Read the current structure and place the guidance in the semantically correct location.
- A session finds a reason NOT to delete a handoff in the same session. Report the scenario so the guidance can be refined or an exception documented.

