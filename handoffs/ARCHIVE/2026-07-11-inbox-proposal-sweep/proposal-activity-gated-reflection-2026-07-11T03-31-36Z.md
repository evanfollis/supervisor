---
from: synthesis-translator
to: general
date: 2026-07-11T03:31:36Z
priority: high
task_id: synthesis-activity-gated-reflection
source_synthesis: /opt/workspace/runtime/.meta/cross-cutting-2026-07-11T03-27-25Z.md
source_proposal: P2 — Activity-gated reflection for idle projects
---

# P2 — Activity-gated reflection for idle projects

## Proposal

**Type:** `reflect.sh` amendment. Skip with carry-forward note when no attended session since last reflection and prior observations are identical.

**Rationale:** P2 (activity-gated reflection) would reduce redundant synthesis output to carry-forward notes per project per observation set. The synthesis is running at full diagnostic cadence against a system with zero execution throughput. The ratio of novel signal to repeated diagnosis is approximately 1:50 per cycle.

**Blast radius:** All reflected projects.

## Verification before action (required)

- Check `/opt/workspace/supervisor/scripts/lib/reflect.sh` for existing activity-gate logic (search for "attended" or "activity").
- If present, this proposal is already landed — write a completion report and close.
- If not present, proceed with the amendment.

## Acceptance criteria

- `reflect.sh` is amended to short-circuit reflection when:
  - No attended session has occurred since the last reflection for this project, AND
  - Prior observations are identical to current observations
- In such cases, the script outputs a carry-forward note instead of regenerating the full reflection.
- Commit with message explaining the optimization (synthesis C137, P2).
- Completion report at `runtime/.handoff/general-proposal-activity-gated-reflection-complete-2026-07-11T03-31-36Z.md`.

## Escalation

None anticipated. This is a computational optimization. If implementation reveals a blocker (e.g., state tracking is not available), escalate the specific constraint.
