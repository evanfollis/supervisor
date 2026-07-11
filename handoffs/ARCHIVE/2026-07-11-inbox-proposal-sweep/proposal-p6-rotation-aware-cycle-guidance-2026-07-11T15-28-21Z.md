---
from: synthesis-translator
to: general
date: 2026-07-11T15:28:21Z
priority: medium
task_id: synthesis-p6-rotation-aware-cycle-guidance
source_synthesis: /opt/workspace/runtime/.meta/cross-cutting-2026-07-11T15-24-30Z.md
source_proposal: P6 (CARRY — C130, 9th cycle) — Rotation-aware cycle-count guidance
---

# P6 — Rotation-aware cycle-count guidance

**Type:** CLAUDE.md amendment or reflection template note.

**Blast radius:** Atlas reflections. Informational.

## Context

Atlas reflections report cycle counts (e.g. "T27", "T28") based on consecutive idle windows. When atlas shifts to a new operator (rotation or handoff), the cycle counter should reset or include rotation-awareness guidance so the receiving operator doesn't inherit ambiguous cycle histories.

## Rationale

Cycle counts inform carry-forward escalation logic. A reflection that reports "T28" without context for a rotation can create false impressions about the age of pending items.

## Verification before action (required)

- Read the latest atlas reflection files in `/opt/workspace/runtime/.meta/`.
- Check if atlas reflections currently note rotation transitions or cycle resets.
- Read `/opt/workspace/supervisor/scripts/lib/reflect-prompt.md` (atlas-specific variant if it exists) to see current guidance.

## Acceptance criteria

- CLAUDE.md or reflect-prompt.md is amended with explicit guidance on rotation-aware cycle counting.
- Atlas reflections can correctly report cycle history across rotations without ambiguity.
- Change committed with message explaining the rotation-awareness rationale.
- Adversarial review via `supervisor/scripts/lib/adversarial-review.sh` (low priority).

## Escalation

If the amendment conflicts with a different cycle-tracking scheme (e.g. a global counter that persists across rotations), escalate with the conflict named.
