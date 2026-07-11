---
from: synthesis-translator
to: general
date: 2026-06-19T15:31:56Z
priority: high
task_id: synthesis-escalation-routing-fix
source_synthesis: /opt/workspace/runtime/.meta/cross-cutting-2026-06-19T15-27-31Z.md
source_proposal: 2. P-escalation-routing-fix
---

# P-escalation-routing-fix — CLAUDE.md amendment + general session reentry

**Carried from C104. 6 cycles open. 7 active URGENTs currently structurally invisible.**

## Problem

7 active URGENTs in `runtime/.handoff/` are invisible to the general session (which reads only `supervisor/handoffs/INBOX/`). The routing split means automated escalations never reach the human. INBOX has grown to 218 items with 5 URGENTs, 2+ of which are 41+ days old.

## Solution

Add `runtime/.handoff/URGENT-*` to the general session's scan path in `/opt/workspace/CLAUDE.md`.

**Location:** `/opt/workspace/CLAUDE.md`, Session Awareness section  
**Change:** Amend the handoff-reading instructions to include scanning both:
- `supervisor/handoffs/INBOX/`
- `runtime/.handoff/URGENT-*`

## Blast radius

All projects (CLAUDE.md is workspace-level). Opt-in (requires manual landing). Once landed, future S3-P2 URGENTs become deliverable to human attention.

## Specification

Update the session awareness documentation to clarify that the general session must scan both:
1. `/opt/workspace/supervisor/handoffs/INBOX/` (existing)
2. `/opt/workspace/runtime/.handoff/URGENT-*` (new)

Reference: standing recommendation #26 in the synthesis.

## Verification before action (required)

- Read `/opt/workspace/CLAUDE.md`, Session Awareness section. Check if `runtime/.handoff/URGENT-*` is already mentioned in the scan path.
- If yes, write a completion report saying "already landed in CLAUDE.md" and close.

## Acceptance criteria

- CLAUDE.md updated to include `runtime/.handoff/URGENT-*` in the general session's scan path.
- Change committed with message explaining the synthesis source and the 6-cycle carry-forward.
- Completion report at `runtime/.handoff/general-supervisor-synthesis-escalation-routing-fix-complete-<iso>.md` pointing back to this handoff and the source synthesis.

## Note

This is step #3 of the critical path (after #1 and #2). It makes future URGENTs visible to the executive for dispatch.

## Escalation

URGENT if:
- The routing fix has already landed by another path. Write a brief completion report saying "obsolete — already landed" and close.
- The fix conflicts with a more recent decision about INBOX vs runtime/.handoff routing. Escalate with the conflict named.
