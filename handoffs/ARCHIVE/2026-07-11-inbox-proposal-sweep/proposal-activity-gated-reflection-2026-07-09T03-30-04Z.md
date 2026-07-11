---
from: synthesis-translator
to: general
date: 2026-07-09T03:30:04Z
priority: high
task_id: synthesis-activity-gated-reflection
source_synthesis: /opt/workspace/runtime/.meta/cross-cutting-2026-07-09T03-26-11Z.md
source_proposal: P2 — Activity-gated reflection for idle projects
---

# P2: Activity-gated reflection for idle projects

**Type:** `reflect.sh` amendment — skip with carry-forward note when no attended session since last reflection and prior observations are identical.

**Rationale:** 12 of 16 reflections correctly short-circuit on no activity. The remaining 4 (atlas, supervisor) produce diminishing-return diagnostics. T23 and T22 are ~90% identical; C73 and C72 are ~85% identical. Activity-gating would suppress the structurally identical re-reports without suppressing novel findings.

**Blast radius:** All reflected projects (opt-in via `projects.conf`).

---

## Verification before action (required)

- Read `/opt/workspace/supervisor/scripts/lib/reflect.sh` around the activity-gate logic (lines where short-circuit checks occur).
- Search for existing carry-forward notes in reflection template to understand the pattern.
- Verify that 12 of the last 16 reflections short-circuited (check `runtime/.meta/` for the reflection files). This confirms the mechanism partially exists.
- If full activity-gate logic already exists, write completion report "already landed in-file" and close.

## Acceptance criteria

- `reflect.sh` detects: no attended session since last reflection AND prior observations are structurally identical (diff-similarity check).
- When both true: emit a carry-forward note (naming prior reflection + observation summary) instead of re-running full reflection.
- Carry-forward note stored in the new reflection file so it's visible in `.meta/` directory.
- Change committed with clear message: "Implement activity-gated reflection for idle projects per synthesis #133"
- Completion report at `/opt/workspace/supervisor/handoffs/INBOX/general-supervisor-synthesis-activity-gated-reflection-complete-<iso>.md`.

## Escalation

URGENT if:
- The activity-gate logic would mask genuine state changes (e.g., a project's git history changed between reflections, but no attended session detected). Escalate with the state change example.
- Diff-similarity threshold is ambiguous. Clarify in the implementation comment before landing.
