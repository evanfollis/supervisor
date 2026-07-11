---
from: synthesis-translator
to: general
date: 2026-07-08T03:29:05Z
priority: medium
task_id: synthesis-activity-gated-reflection
source_synthesis: /opt/workspace/runtime/.meta/cross-cutting-2026-07-08T03-24-41Z.md
source_proposal: P2 — Activity-gated reflection
---

# P2: Activity-gated reflection for idle windows

**Type:** `reflect.sh` amendment — skip with carry-forward note when no attended session since last reflection and prior observations are identical.

**Current behavior:** All reflections run if they are invoked, producing repetitive diagnostics in idle windows.

**Proposed behavior:** Short-circuit if:
1. No commits to the project since last reflection
2. No telemetry events for the project since last reflection
3. No session JSONL activity since last reflection
4. Prior reflection output is structurally identical to this run's diagnostic state

When all conditions are met, emit a carry-forward note instead of re-running the full reflection.

**Rationale:** 12 of 16 reflections already short-circuit correctly on no activity. The remaining 4 (atlas, supervisor) produce increasingly repetitive diagnostics in idle windows. Activity-gating would not suppress novel findings (atlas T20's `skipped_unreplayable` discovery proves the current system can still extract new signal even in low-activity windows), but would suppress structurally identical re-reports that waste token budget and dilute signal quality.

**Blast radius:** All reflected projects (opt-in via `projects.conf`). ~30 min implementation.

**Carry history:** Proposal from C114 (18th cycle). 39 cycles open as of C131.

## Verification before action (required)

- Check `/opt/workspace/supervisor/scripts/lib/reflect.sh` lines 69-73 where short-circuit currently happens
- Verify the activity check logic is working: should exit 0 and emit "short-circuit (no commits, no telemetry, no session activity)"
- Check whether `atlas-reflection` and `supervisor-reflection` are still the only projects producing repetitive idle diagnostics

## Acceptance criteria

- `reflect.sh` amended to detect identical-state idle windows and emit carry-forward note instead of re-running
- Short-circuit note should be distinguishable from "no activity at all" — include counter from prior reflection
- Change committed with message explaining why identical-state detection improves signal quality
- Completion report written to `/opt/workspace/runtime/.handoff/general-supervisor-synthesis-activity-gated-reflection-complete-<iso>.md`

## Escalation

URGENT if:
- The short-circuit logic inadvertently suppresses a novel discovery (e.g. a reflection that says "same as last time" but has a new Finding section)
- Implementation requires changes to reflection state store or template — document the schema change
