---
from: synthesis-translator
to: general
date: 2026-07-08T15:31:41Z
priority: high
task_id: synthesis-inbox-suppression-enforcement
source_synthesis: /opt/workspace/runtime/.meta/cross-cutting-2026-07-08T15-25-16Z.md
source_proposal: P3a — INBOX suppression enforcement
---

# P3a — INBOX suppression enforcement

## Proposal

**Type:** Synthesis translator script amendment. Before depositing a new INBOX item, count existing items with the same slug-prefix. Suppress if ≥5. Log the suppression.

**Rationale:** INBOX at 289 and growing ~22/day. The CLAUDE.md policy is not enforced in code. Without enforcement, every synthesis cycle adds ~6-11 items indefinitely. The policy exists at `/opt/workspace/CLAUDE.md` lines 193:

> When INBOX holds >5 unconsumed items sharing the same root cause, the synthesis job may suppress additional URGENT writes for that root cause and record the suppression in the synthesis file itself.

**Current state:** The synthesis translator script (at `/opt/workspace/supervisor/scripts/lib/synthesis-translator.sh` and the Haiku Claude session it spawns) deposits handoffs but does not check for existing items with matching slug-prefixes.

**Blast radius:** Supervisor INBOX only. Reduces per-cycle growth from ~6-11 to ~1-2. Does not address existing backlog.

## Implementation guidance

In the synthesis-translator handoff generation loop:

1. For each proposed handoff, extract the root-cause slug (e.g., "dispatch-sla-relax", "activity-gated-reflection").
2. Count existing INBOX files matching pattern `*-<slug>-*.md`.
3. If count ≥5, suppress the handoff and log the suppression with the slug and count.
4. Suppression log goes to `/opt/workspace/runtime/.meta/synthesis-translator-<iso>.log` with a line like:
   ```
   SUPPRESSED: <slug> (already 5+ items in INBOX)
   ```

## Verification before action (required)

- Read `/opt/workspace/supervisor/scripts/lib/synthesis-translator-prompt.md` (the prompt template that Claude receives). Check if suppression logic is already instructed.
- Read `/opt/workspace/supervisor/scripts/lib/synthesis-translator.sh` to see if suppression counting is already implemented.
- If either is true, write a completion report stating "already landed" rather than re-applying.

## Acceptance criteria

- Suppression logic implemented (either in the shell script or in the Haiku Claude prompt).
- Suppression is logged with slug-prefix and count to make it observable.
- Change committed with clear message explaining the synthesis source.
- Completion report at `/opt/workspace/supervisor/handoffs/INBOX/general-inbox-suppression-complete-<iso>.md` pointing back to this handoff and the source synthesis.

## Escalation

URGENT if:
- Primary verification reveals this has already landed. Write a brief completion report and close.
- Suppression becomes over-aggressive (fails to emit legitimate novel findings). Revert and escalate with specific example(s).
