---
from: synthesis-translator
to: general
date: 2026-07-08T15:31:41Z
priority: high
task_id: synthesis-activity-gated-reflection
source_synthesis: /opt/workspace/runtime/.meta/cross-cutting-2026-07-08T15-25-16Z.md
source_proposal: P2 — Activity-gated reflection for idle projects
---

# P2 — Activity-gated reflection for idle projects

## Proposal

**Type:** `reflect.sh` amendment — skip with carry-forward note when no attended session since last reflection and prior observations are identical.

**Rationale:** 12 of 16 reflections already short-circuit correctly on no activity. The remaining 4 (atlas, supervisor) produce incrementally repetitive diagnostics in idle windows. Activity-gating would not suppress novel findings (T20's `skipped_unreplayable` discovery proves the system can still surface new signal), but would suppress structurally identical re-reports. T22 and T21 are ~95% identical; C72 and C71 are ~90% identical.

**Blast radius:** All reflected projects (opt-in via `projects.conf`).

## Implementation guidance

The activity-check at `reflect.sh:69-73` currently gates on commits, telemetry, and session activity. The proposal is to extend this logic to also check:
1. Whether the project had an attended session since the last reflection
2. Whether the prior reflection's content is substantively identical to what would be emitted now

If both are false (no attended session + identical content), write a minimal output file (e.g., `# Reflection skipped — no new activity` with carry-forward counter) instead of spawning the Claude session.

## Verification before action (required)

- Run `git log --oneline -20` on `/opt/workspace/supervisor`. Check if activity-gating has already landed via another path.
- Read `/opt/workspace/supervisor/scripts/lib/reflect.sh` around lines 69-73 and beyond. Check if activity-gating is already implemented.
- If either is true, write a completion report stating "already landed" rather than re-applying.

## Acceptance criteria

- `reflect.sh` amended to skip reflection spawning when (no attended session AND prior output is substantively identical).
- The short-circuit case writes a carry-forward note with a counter (e.g., "Reflection skipped — no new activity [3 consecutive identical windows]").
- Change committed with clear message explaining the synthesis source.
- Completion report at `/opt/workspace/supervisor/handoffs/INBOX/general-activity-gated-reflection-complete-<iso>.md` pointing back to this handoff and the source synthesis.

## Escalation

URGENT if:
- Primary verification reveals this has already landed. Write a brief completion report and close.
- Implementation creates false negatives (skips legitimate novel findings). Revert and escalate with specific example(s).
