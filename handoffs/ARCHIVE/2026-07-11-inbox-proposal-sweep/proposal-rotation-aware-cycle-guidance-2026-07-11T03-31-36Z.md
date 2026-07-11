---
from: synthesis-translator
to: general
date: 2026-07-11T03:31:36Z
priority: medium
task_id: synthesis-rotation-aware-cycle-guidance
source_synthesis: /opt/workspace/runtime/.meta/cross-cutting-2026-07-11T03-27-25Z.md
source_proposal: P6 — Rotation-aware cycle-count guidance
---

# P6 — Rotation-aware cycle-count guidance

## Proposal

**Type:** CLAUDE.md amendment or reflection template note.

**Rationale:** Atlas reflections use a cycle counter that is not rotation-aware. When reporting cycle-N alongside atlas bucket deadlines and consecutive-window counts, the guidance should distinguish between "the workspace has been running for N cycles" and "atlas has been in the current rotation for N cycles." This prevents cold-start readers from misinterpreting stale cycle counts in updated synthesis files.

**Blast radius:** Atlas reflections. Informational.

## Verification before action (required)

- Check `/opt/workspace/CLAUDE.md` for any existing rotation-aware cycle guidance in the Atlas sections or "Automated Self-Reflection Loop" section.
- Check `/opt/workspace/supervisor/scripts/lib/` for reflection templates and see if rotation context is already documented.
- If rotation-aware guidance is present, this proposal is landed — write a completion report and close.
- If absent, proceed with the amendment.

## Acceptance criteria

- Either:
  1. CLAUDE.md is amended to include rotation-aware cycle-count guidance in the atlas reflection instructions, OR
  2. The reflection template for atlas (if separate) is amended to document the rotation context
- The guidance clarifies that cycle counts are workspace-global unless otherwise noted.
- Commit with message explaining the cycle-count guidance (synthesis C137, P6).
- Completion report at `runtime/.handoff/general-proposal-rotation-aware-cycle-guidance-complete-2026-07-11T03-31-36Z.md`.

## Escalation

None anticipated. This is informational guidance. If the structure of atlas cycle tracking is unclear, review atlas reflections in `/opt/workspace/runtime/.meta/` to understand the current reporting pattern.
