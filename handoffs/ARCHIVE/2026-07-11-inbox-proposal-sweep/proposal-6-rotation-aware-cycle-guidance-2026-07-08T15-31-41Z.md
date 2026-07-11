---
from: synthesis-translator
to: general
date: 2026-07-08T15:31:41Z
priority: medium
task_id: synthesis-rotation-aware-cycle-guidance
source_synthesis: /opt/workspace/runtime/.meta/cross-cutting-2026-07-08T15-25-16Z.md
source_proposal: P6 — Add rotation-aware cycle-count guidance
---

# P6 — Add rotation-aware cycle-count guidance

## Proposal

**Type:** CLAUDE.md amendment or reflection template note.

**Rationale:** Atlas reflections track `consecutive_empty_count` across the reflection rotation boundary. When the runner cycles through multiple prediction windows (buckets), the counter resets without explanation, making it ambiguous whether a high count represents a long idle or a reset due to rotation. Adding guidance on how to interpret the counter across rotation boundaries would reduce confusion.

**Context:** Atlas T22 tracked `consecutive_empty_count: 598` successfully, but the reflection template could benefit from an explicit note that this counter may reset on rotation. This is informational and low-risk.

**Blast radius:** Atlas reflections. Low-risk, informational.

## Implementation guidance

Add a note to either:
1. `/opt/workspace/CLAUDE.md` in the Automated Self-Reflection Loop section, or
2. `/opt/workspace/supervisor/scripts/lib/reflect-prompt.md` (the reflection template), or
3. The atlas-specific reflection prompt

The note should explain: "When reflecting on projects with rotation-based execution (e.g., atlas with prediction buckets), `consecutive_empty_count` may reset at rotation boundaries. Interpret high counts in context of the current rotation window, not across windows. If a counter resets unexpectedly, check the prior reflection for rotation context."

## Verification before action (required)

- Read `/opt/workspace/CLAUDE.md` to check if rotation guidance is already present.
- Read `/opt/workspace/supervisor/scripts/lib/reflect-prompt.md` to check if guidance is already present.
- Read the atlas-specific reflection template (if one exists) to check for existing guidance.
- If any of these already contain rotation guidance, write a completion report stating "already landed" rather than re-applying.

## Acceptance criteria

- Rotation-aware guidance added to at least one canonical location.
- Guidance is clear and helpful (not overly technical or verbose).
- Change committed with clear message explaining the synthesis source.
- Completion report at `/opt/workspace/supervisor/handoffs/INBOX/general-rotation-guidance-complete-<iso>.md` pointing back to this handoff and the source synthesis.

## Escalation

URGENT if:
- Primary verification reveals this has already landed. Write a brief completion report and close.
- The guidance is unclear or contradicts existing patterns in the reflection templates. Escalate with specific example(s).
