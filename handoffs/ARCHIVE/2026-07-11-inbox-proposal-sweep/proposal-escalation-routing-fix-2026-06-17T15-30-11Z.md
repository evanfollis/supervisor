---
from: synthesis-translator
to: general
date: 2026-06-17T15:30:11Z
priority: high
task_id: synthesis-escalation-routing-fix
source_synthesis: /opt/workspace/runtime/.meta/cross-cutting-2026-06-17T15-26-36Z.md
source_proposal: Proposal 2 — P-escalation-routing-fix (carry from C103 — 2nd cycle)
---

# P-escalation-routing-fix (Pattern 3: Escalation routing architecturally broken)

**Type:** CLAUDE.md amendment.
**File:** `/opt/workspace/CLAUDE.md`, section "Session Awareness" (update general session startup procedure).
**Blast radius:** General session only. Behavioral guidance. Low risk.
**Status:** 2nd cycle. Immediately makes 7 existing URGENT files visible.

Currently, the general session checks for URGENT files only in `supervisor/handoffs/INBOX/`. However, 7 URGENT files from project sessions are sitting unread in `runtime/.handoff/URGENT-*`. These are structurally invisible to the executive surface because the startup procedure doesn't check that path.

**Proposed CLAUDE.md delta:**
```markdown
- If you are the `general` session, on startup also check for URGENT
  files in `runtime/.handoff/`: `ls /opt/workspace/runtime/.handoff/URGENT-* 2>/dev/null`
  Process these with the same priority as `supervisor/handoffs/INBOX/` URGENTs.
```

The amendment goes in the "Session Awareness" section under the reentry procedure. Add the new check to the existing startup guidance where the general session reads handoffs.

## Verification before action (required)

- Read `/opt/workspace/CLAUDE.md`, look for existing guidance about checking for handoffs in Session Awareness.
- Check if the routing check for `runtime/.handoff/URGENT-*` is already documented.
- If it is, write a completion report "already in CLAUDE.md" rather than re-adding.

## Acceptance criteria

- The amendment is added to the "Session Awareness" section of `/opt/workspace/CLAUDE.md`.
- The amendment instructs the `general` session to check `runtime/.handoff/URGENT-*` on startup with the same priority as INBOX URGENTs.
- Change committed with message: "Amend CLAUDE.md: general session checks runtime/.handoff/URGENT-* on startup (routing fix)"
- No adversarial review required (configuration/guidance update, low complexity).
- Completion report at `runtime/.handoff/general-general-synthesis-escalation-routing-fix-complete-<iso>.md` pointing back to this handoff and the source synthesis.

## Escalation

URGENT if:
- Verification reveals the amendment is already in place. Write "already in CLAUDE.md" completion report and close.
- The amendment conflicts with a more recent CLAUDE.md revision. Do not force-apply; escalate with the conflict named.

---

**Pattern context:** This is Pattern 3 (Split-brain routing + total escalation surface neglect) from the synthesis. The synthesis detected 8 URGENT files across two paths (`runtime/.handoff/` and `supervisor/handoffs/INBOX/`), with no attended executive session processing them in 12 cycles. The root cause is split routing (this fix) plus total escalation surface neglect (the general session not reading INBOX either). This fix makes the URGENT files visible; the general session's responsibility to read them is separate.
