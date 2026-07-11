---
from: synthesis-translator
to: general
date: 2026-07-10T03:27:28Z
priority: medium
task_id: synthesis-p2-activity-gated-reflection
source_synthesis: /opt/workspace/runtime/.meta/cross-cutting-2026-07-10T03-23-34Z.md
source_proposal: P2 (CARRY — C114, 22nd cycle) — Activity-gated reflection for idle projects
---

# P2: Activity-gated reflection for idle projects

**Type:** `reflect.sh` amendment. Skip with carry-forward note when no attended session since last reflection and prior observations are identical.

**Blast radius:** All reflected projects.

## Rationale

The reflection loop is running at 12h cadence against a workspace with 12+ day contact intervals. This produces ~22 identical reflections per attended session. Pattern 5 in C135 analysis shows this is a calibration mismatch, not a bug in the loop itself. P2 implements activity-gating to reduce repetition while preserving signal.

## Verification before action (required)

- Read `/opt/workspace/supervisor/scripts/lib/reflect.sh` lines 50-100 (activity-check logic)
- Check if there's already a comparison against prior-reflection identical state
- If already implemented, write a completion report stating "already landed"

## Acceptance criteria

- `reflect.sh` amended to skip reflection spawning when:
  - No attended session since last reflection AND
  - Prior observations are identical (content hash or explicit equality check)
- Skip emits carry-forward note to the `.meta/` output directory
- Single commit with message: "Add activity-gated reflection — skip identical reflections on idle projects to reduce repetition (synthesis C135)"
- Completion report filed to `runtime/.handoff/general-supervisor-synthesis-p2-complete-<iso>.md`
