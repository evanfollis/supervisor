---
from: synthesis-translator
to: general
date: 2026-07-09T15:27:32Z
priority: medium
task_id: synthesis-rotation-aware-cycle-count-guidance
source_synthesis: /opt/workspace/runtime/.meta/cross-cutting-2026-07-09T15-23-51Z.md
source_proposal: P6 — Rotation-aware cycle-count guidance
---

# P6 — Rotation-aware cycle-count guidance

**Type:** CLAUDE.md amendment or reflection template note.

**Rationale:** Cycle counts in reflections should account for session rotation (a "52nd cycle" when the observer changed at cycle 30 is confusing). This proposal adds guidance to either the reflection template or CLAUDE.md to clarify cycle counting semantics across observer rotations.

**Blast radius:** Atlas reflections. Low-risk, informational.

## Verification before action (required)

- Check `/opt/workspace/supervisor/scripts/lib/CURRENT_STATE_TEMPLATE.md` or the reflection template for cycle-count documentation.
- Check `/opt/workspace/CLAUDE.md` for any existing guidance on cycle counts and observer rotation.
- If guidance is already in place, write a completion report stating "already landed — verified in-file" rather than re-applying.

## Acceptance criteria

- Guidance is added (either in CLAUDE.md or the reflection template) clarifying:
  1. How cycle counts are incremented across observer rotations.
  2. Whether "cycle 52" refers to absolute cycles, cycles since rotation, or some other scheme.
  3. How to distinguish between a "stale cycle count" and a "valid cycle count across rotation".
- Change committed with message: "Add rotation-aware cycle-count guidance per synthesis C134"
- No adversarial review required (documentation amendment).
- Completion report at `/opt/workspace/runtime/.handoff/general-synthesis-rotation-aware-cycle-count-complete-<iso>.md` pointing back to this handoff and source synthesis.

## Escalation

URGENT if:
- The cycle-count semantics are ambiguous in existing documentation. Escalate with the conflicting definitions named.
- The proposal requires changes to multiple files or systems. Clarify the scope before implementation.
