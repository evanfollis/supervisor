---
from: synthesis-translator
to: general
date: 2026-06-12T15:31:48Z
priority: high
task_id: synthesis-handoff-resolution-checklist
source_synthesis: /opt/workspace/runtime/.meta/cross-cutting-2026-06-12T15-27-51Z.md
source_proposal: 2. P-handoff-resolution-checklist (carry from C93 — 2nd cycle)
---

# P-handoff-resolution-checklist

**Type:** CLAUDE.md amendment to clarify existing convention.

## The Problem

Stale handoff accumulation is now a chronic workspace condition. Resolved issues have corresponding handoff files that persist for days or weeks because the resolving session deletes them inconsistently — deletion gets deferred to "a future session," which never happens because that session has no context to confirm the issue is closed.

| Stale handoff | Resolved | Cycles flagged |
|--------------|----------|----------------|
| `URGENT-atlas-unpushed-commits-3rd-cycle.md` | Jun 11 ~20:31Z | 4 reflection cycles |
| `general-m5-current-state-untouched-command-*.md` | Jun 10 | 5 reflection cycles |
| `context-repository-auth-failure-diagnosis-*.md` | ~23 days ago | ~40 days on disk |
| `context-repository-current-state-commit-discipline-*.md` (×2) | ~20 days ago | ~30 days on disk |
| Landed INBOX proposals (P2, P-reflect-prompt) | Jun 11 16:03Z | 2 cycles |

This is evidence of a lifecycle gap: handoff files have a creation mechanism but no automated or reliably-triggered close mechanism.

## The Fix

**File:** `/opt/workspace/supervisor/CLAUDE.md`
**Section:** "Session Awareness", after the existing line "After reading and acting on a handoff, delete the file."

**Proposed addition:**

```markdown
- **When resolving an issue that has a corresponding handoff or URGENT file, delete the handoff file in the same session.** Do not defer cleanup to a future session. The resolving session has the context to confirm the issue is closed; a future session must re-derive that context from scratch, which consistently fails to happen.
```

This elevates a convention to an explicit requirement and explains why (context locality).

## Workspace Impact

- **Blast radius:** All projects. Behavioral guidance (not enforcement).
- **Effort:** <5 minutes
- **Credentials:** Zero
- **Risk:** Zero — clarifies existing convention without enforcement. Low-friction guidance.
- **Leverage:** Moderate. Addresses a structural cleanup gap. Combined with other proposals, prevents reflection loops from becoming noise factories.

## Verification Before Action

```bash
# Confirm the current CLAUDE.md text exists but the clarification doesn't:
grep -n "After reading and acting on a handoff, delete the file" /opt/workspace/supervisor/CLAUDE.md
# Should find the line

grep -n "When resolving an issue that has a corresponding handoff" /opt/workspace/supervisor/CLAUDE.md
# Should NOT find this (it's the new text)
```

## Acceptance Criteria

- The new guidance is added immediately after the existing "delete the file" line
- The text explains both the requirement and the reason (context locality)
- Commit message references this proposal and the synthesis cycle
- No enforcement mechanism is added (this is guidance, not automation)

## Escalation

URGENT if:
- This conflicts with a more recent decision in `supervisor/decisions/`
- A pattern emerges that handoffs are being deliberately preserved (would indicate the convention needs different handling)
- Principal has stated a different policy on handoff cleanup recently

---

**Why this matters now:** Six reflection cycles have flagged stale handoffs. This is the third synthesis cycle carrying this proposal. The fix is a single paragraph that clarifies what should already be happening. C93 proposed it; C94 confirms the problem persists and requests permission to enforce shorter reflection cycles (P-reflection-short-circuit). Stale handoffs are evidence the convention is not self-sustaining.
