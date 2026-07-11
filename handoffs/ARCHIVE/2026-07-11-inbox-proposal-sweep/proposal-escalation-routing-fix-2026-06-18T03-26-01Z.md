---
from: synthesis-translator
to: general
date: 2026-06-18T03:26:01Z
priority: high
task_id: synthesis-P-escalation-routing-fix
source_synthesis: /opt/workspace/runtime/.meta/cross-cutting-2026-06-18T03-23-11Z.md
source_proposal: Proposal 2 — P-escalation-routing-fix (carry from C103 — 3rd cycle)
---

# P-escalation-routing-fix (C103 → C104 → C105)

## Proposal (from C104)

**Type:** CLAUDE.md amendment + session behavior guidance.
**Section:** "Session Awareness" in `/opt/workspace/CLAUDE.md`.

**Proposed CLAUDE.md delta:**
```markdown
- If you are the `general` session, on startup also check for URGENT
  files in `runtime/.handoff/`: `ls /opt/workspace/runtime/.handoff/URGENT-* 2>/dev/null`
  Process these with the same priority as `supervisor/handoffs/INBOX/` URGENTs.
```

**Blast radius:** General session only. Behavioral guidance. Low risk.
**Status:** 3rd synthesis cycle (C105). Immediately makes 7 existing URGENT files visible and actionable.

## Why this matters

Pattern 3 (escalation routing broken): 7-8 URGENT files sit in `runtime/.handoff/` structurally invisible to the general session. Meanwhile, `supervisor/handoffs/INBOX/` also holds unprocessed URGENTs. The routing mismatch + total escalation surface neglect means critical blockers are unread.

This amendment tells the general session to scan both surfaces on startup.

## Verification before action (required)

- Check `/opt/workspace/runtime/.handoff/` for URGENT files: `ls /opt/workspace/runtime/.handoff/URGENT-*`. Confirm >0 exist.
- Read `/opt/workspace/CLAUDE.md`. Check "Session Awareness" section. Verify the proposed text is NOT already there.
- If already landed, write a completion report stating "already present in CLAUDE.md" rather than re-adding.

## Acceptance criteria

- CLAUDE.md amended in "Session Awareness" section with the exact text above.
- Change committed with clear message: "Route runtime/.handoff/ URGENTs to general session startup".
- No code changes required — this is documentation/behavioral guidance only.
- Completion report at `supervisor/handoffs/INBOX/general-escalation-routing-fix-complete-<iso>.md`.

## Notes

This is a prerequisite for Pattern 3's second half: the general session must actually READ the INBOX once URGENTs are routable. After this amendment lands, follow-up escalation work should confirm the general session is processing them.

---

**C105 context:** This proposal is in its 3rd cycle. It is necessary but not sufficient — routing visibility alone doesn't fix escalation-surface neglect if the general session doesn't attend them. Resolution unblocks future URGENT deliverability.
