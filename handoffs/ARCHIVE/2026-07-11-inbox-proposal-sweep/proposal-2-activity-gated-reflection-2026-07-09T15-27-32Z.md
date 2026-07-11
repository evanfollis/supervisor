---
from: synthesis-translator
to: general
date: 2026-07-09T15:27:32Z
priority: high
task_id: synthesis-activity-gated-reflection
source_synthesis: /opt/workspace/runtime/.meta/cross-cutting-2026-07-09T15-23-51Z.md
source_proposal: P2 — Activity-gated reflection for idle projects
---

# P2 — Activity-gated reflection for idle projects

**Type:** `reflect.sh` amendment — skip with carry-forward note when no attended session since last reflection and prior observations are identical.

**Rationale:** T23/T24 are ~90% identical. C73/C74 are ~85% identical. The substantive reflections are producing diminishing marginal information per cycle.

**Blast radius:** All reflected projects (opt-in via `projects.conf`).

## Verification before action (required)

- Locate `reflect.sh` (likely at `/opt/workspace/supervisor/scripts/lib/reflect.sh`).
- Check if activity-gating logic already exists (grep for `attended_session` or `carry-forward`).
- Read `projects.conf` to understand which projects are opted into reflection.
- If activity-gating is already in place, write a completion report stating "already landed — verified in-code" rather than re-applying.

## Acceptance criteria

- `reflect.sh` is amended to:
  1. Before running a reflection for a project, check if an attended session has touched the repo since the prior reflection.
  2. If no attended session AND prior reflection observations are identical (or near-identical), skip the reflection and emit a carry-forward note.
  3. Log the skip reason to standard output or telemetry.
- The logic respects the opt-in mechanism in `projects.conf`.
- Change committed with message: "Add activity-gated reflection for idle projects per synthesis C134"
- Adversarial review via `supervisor/scripts/lib/adversarial-review.sh` (edge cases: what counts as "attended session"? How is identity match computed for prior observations?).
- Completion report at `/opt/workspace/runtime/.handoff/general-synthesis-activity-gated-reflection-complete-<iso>.md` pointing back to this handoff and source synthesis.

## Escalation

URGENT if:
- The definition of "attended session" is ambiguous (automated commits? manual pushes? shell commands?). Clarify before implementing.
- The "identical observations" check requires fuzzy matching. Specify the matching logic (line-by-line diff? hash of key fields?).
- The change would skip reflections for projects where this is not safe (e.g., highly volatile projects). Verify with project maintainers.
