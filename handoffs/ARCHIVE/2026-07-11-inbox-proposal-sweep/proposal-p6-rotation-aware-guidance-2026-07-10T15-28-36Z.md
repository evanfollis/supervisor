---
from: synthesis-translator
to: general
date: 2026-07-10T15:28:36Z
priority: low
task_id: synthesis-p6-rotation-aware-guidance
source_synthesis: /opt/workspace/runtime/.meta/cross-cutting-2026-07-10T15-24-51Z.md
source_proposal: P6 (CARRY — C130, 7th cycle): Rotation-aware cycle-count guidance
---

# P6: Rotation-aware cycle-count guidance

**Type:** CLAUDE.md amendment or reflection template note.

**Blast radius:** Atlas reflections. Informational.

## Background

Atlas reflections emit cycle-count tracking (e.g., "25th idle window", "26th idle window"). When the reflection system is under heavy load or when sessions rotate, these counts can become misleading if not contextualized.

The proposal is to add guidance to atlas reflection prompts or to CLAUDE.md to help interpret cycle-counts in the presence of reflection cycles that may have been skipped, carried forward, or emitted by a different session.

This is primarily informational/documentary — not a structural fix.

## Verification before action (required)

- Determine target location: atlas reflection prompt template (`reflect-prompt.md` or project-specific override?) or CLAUDE.md?
- Check: Does the current reflection template already have cycle-count guidance?
- Search: `grep -r "rotation\|cycle-count\|cycle.*guidance" /opt/workspace/supervisor/`

## Implementation notes

The guidance should clarify:

1. Cycle counts may skip when a project has no activity (P2 carry-forward)
2. Carry-forward reflections are labeled and don't increment the cycle count
3. Attended sessions will show a jump in cycle counts if prior idle cycles were skipped
4. This is not a bug; it's expected and improves signal-to-noise

Example text for reflection template or CLAUDE.md:
```
Note on cycle counting: If prior reflections show a gap in cycle numbers 
(e.g., T24 followed by T26), those skipped cycles had no activity and were 
carry-forwarded. This is expected. Cycle counts reflect "times reflection was 
invoked" not "absolute elapsed time".
```

## Acceptance criteria

- Guidance text added to either:
  - `/opt/workspace/supervisor/scripts/lib/reflect-prompt.md` (general)
  - `/opt/workspace/CLAUDE.md` under a new section "Reflection cycle-count interpretation"
- Explanation is clear and doesn't add confusion
- Change committed with message: "Add rotation-aware cycle-count guidance for atlas reflections"
- Completion report filed at `runtime/.handoff/general-rotation-guidance-complete-<iso>.md`

## Escalation

This is a documentation/guidance task. If there's uncertainty about where to place it (prompt vs. CLAUDE.md vs. somewhere else), escalate for placement guidance before committing.
