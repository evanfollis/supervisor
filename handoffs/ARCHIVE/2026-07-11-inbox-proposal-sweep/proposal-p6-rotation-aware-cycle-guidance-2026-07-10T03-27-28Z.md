---
from: synthesis-translator
to: general
date: 2026-07-10T03:27:28Z
priority: low
task_id: synthesis-p6-rotation-aware-cycles
source_synthesis: /opt/workspace/runtime/.meta/cross-cutting-2026-07-10T03-23-34Z.md
source_proposal: P6 (CARRY — C130, 6th cycle) — Rotation-aware cycle-count guidance
---

# P6: Rotation-aware cycle-count guidance

**Type:** CLAUDE.md amendment or reflection template note.

**Blast radius:** Atlas reflections. Informational.

## Rationale

Atlas reflections reference cycle counts (T24, T25, etc.) that increment sequentially across attended and unattended windows. Long idle periods create ambiguity: is "T25" the 25th cycle since project start, or the 25th *attended* cycle? Rotation-aware guidance clarifies this distinction and provides context for interpreting historical references.

## Verification before action (required)

- Check if atlas-reflection-*.md files already include rotation-aware cycle documentation
- Check if `/opt/workspace/CLAUDE.md` or the reflection template already mentions this pattern
- If already documented, write a completion report stating "already landed"

## Acceptance criteria

- Either CLAUDE.md or the reflection template (`supervisor/scripts/lib/reflect-prompt.md`) amended to define:
  - What "cycle count" represents (total cycles since project inception)
  - What "attended cycle" means (cycles with human interaction)
  - Optional: recommendation to log both in reflection output for clarity
- Single commit with message: "Document rotation-aware cycle-count guidance for atlas reflections (synthesis C135)"
- Completion report filed to `runtime/.handoff/general-supervisor-synthesis-p6-complete-<iso>.md`
