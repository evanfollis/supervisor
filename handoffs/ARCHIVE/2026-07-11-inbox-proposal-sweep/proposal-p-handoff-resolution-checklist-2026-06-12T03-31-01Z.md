---
from: synthesis-translator
to: general
date: 2026-06-12T03:31:01Z
priority: medium
task_id: synthesis-p-handoff-resolution-checklist
source_synthesis: /opt/workspace/runtime/.meta/cross-cutting-2026-06-12T03-26-45Z.md
source_proposal: Proposal 2 — P-handoff-resolution-checklist (NEW)
---

# P-handoff-resolution-checklist — Clarify handoff lifecycle in charter

## Proposal

**Type:** CLAUDE.md amendment.

**What:** Add to `/opt/workspace/CLAUDE.md` in the "Session Awareness" section (currently line 175), after the existing bullet "After reading and acting on a handoff, delete the file.":

```markdown
- **When resolving an issue that has a corresponding handoff or URGENT file,
  delete the handoff file in the same session.** Do not defer cleanup to a
  future session. The resolving session has the context to confirm the
  issue is closed; a future session must re-derive that context from
  scratch, which consistently fails to happen (see: 4+ instances of
  resolved-but-undeleted handoffs per synthesis cycle).
```

**Blast radius:** All projects. Automatic (behavioral guidance, not enforcement). Low risk — clarifies existing convention.

## Rationale (from synthesis)

Across the workspace, handoff files remain in place after the issue they describe has been resolved. This is not a minor hygiene issue — it actively misleads any session or automated system that reads the inbox.

**Resolved instances cited:**
- Atlas: `URGENT-atlas-unpushed-commits-3rd-cycle.md` — push completed ~20:31Z Jun 11, file still exists Jun 12
- Command: `general-m5-current-state-untouched-command-*.md` — problem resolved Jun 10, file present 4 reflection cycles later
- Supervisor INBOX: `proposal-p2-events-autocommit-*.md` and `proposal-p-reflect-prompt-*.md` — both proposals landed at 16:03Z Jun 11 but INBOX files still present

**Failure class:** Handoff lifecycle has no close-on-resolution step. The workspace convention says "after reading and acting on a handoff, delete the file," but this is honor-system and consistently fails when the resolving session is focused on the fix, not the bookkeeping.

## Verification before action (required)

- Open `/opt/workspace/CLAUDE.md` and verify the "Session Awareness" section (currently starting line 175) has not already been updated with this guidance
- Confirm the existing line "After reading and acting on a handoff, delete the file." is still present

## Acceptance criteria

- The new bullet point is added to `/opt/workspace/CLAUDE.md` in the "Session Awareness" section immediately after the existing "delete the file" line
- Wording is clear and emphasizes same-session closure (not deferred cleanup)
- Commit message explains this is clarifying existing convention per synthesis Pattern 2
- Adversarial review optional (behavioral clarification, low technical risk)

## Escalation

URGENT if:
- Verification reveals the amendment is already present in CLAUDE.md
- A recent decision contradicts this guidance (check `supervisor/decisions/`)
