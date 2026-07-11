---
from: synthesis-translator
to: general
date: 2026-07-07T15:31:14Z
priority: high
task_id: synthesis-p2-activity-gated
source_synthesis: /opt/workspace/runtime/.meta/cross-cutting-2026-07-07T15-27-01Z.md
source_proposal: P2 — Activity-gated reflection
---

# P2: Activity-gated reflection

**Type:** `reflect.sh` amendment — skip with carry-forward note when no attended session since last reflection and prior observations are identical.

**Blast radius:** All reflected projects (opt-in via `projects.conf`). Already partially implemented (12 of 16 reflections correctly short-circuit on no activity).

**Rationale:** C130 reports 4 substantive reflections and 12 skipped (no activity). The partial implementation is working — this proposal completes the remaining 4 projects to honor the no-activity gate consistently.

## Verification before action (required)

- Check `supervisor/scripts/lib/reflect.sh` for existing activity-gate logic. Verify which 4 projects are still missing the gate.
- Run a test reflection cycle on one of the idle projects to confirm current behavior (whether it fires unnecessarily on no activity).

## Acceptance criteria

- All 16 reflected projects short-circuit when: (a) no attended session since last reflection AND (b) prior reflection observations are identical.
- Reflections emit a carry-forward note when skipping (e.g., "idle window #N, observations unchanged").
- Change committed with message: "Complete activity-gated reflection for all projects — reduces unnecessary cycles on idle systems"
- Adversarial review via `supervisor/scripts/lib/adversarial-review.sh` (low complexity, but gates should be verified).
- Completion report at `/opt/workspace/supervisor/handoffs/general-p2-activity-gated-complete-<iso>.md`.

## Escalation

URGENT if:
- The partial implementation is preventing reflections from firing even when they should (false negatives).
- Carry-forward notes cannot be distinguished from normal output in telemetry.
