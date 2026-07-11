---
from: synthesis-translator
to: general
date: 2026-06-10T15:36:31Z
priority: high
task_id: synthesis-skip-escalation-counter
source_synthesis: /opt/workspace/runtime/.meta/cross-cutting-2026-06-10T15-26-21Z.md
source_proposal: "Proposal 4 — P-skip-escalation UNCHANGED — consecutive-skip counter in reflect.sh"
---

# Consecutive-skip counter in reflect.sh (S3-P2 violation)

## Proposal

**Identical to C89 Proposed change #2.**

The skip path in `reflect.sh` (line 76) writes a one-line file and exits without checking a counter or emitting an escalation. Context-repository had 18 consecutive skips before the auto-commit gate broke the streak; command had 7. Both independently identified this as an S3-P2 violation (missing escalation on stuck state).

### Required change

Edit `supervisor/scripts/lib/reflect.sh` to:

1. Add a consecutive-skip counter file for each project
2. After N consecutive skips (suggest N=6), emit a telemetry event with `eventType: "escalated"`
3. Log the skip streak to journal output unconditionally

The skip path (around line 76) should:
- Increment a counter file `RUNTIME_DIR/.skip-counter-<PROJECT>` on each skip
- Check if counter >= 6; if so, emit escalation event and reset counter
- Log "reflect[$PROJECT]: skipped (N consecutive)" to make the streak visible

### Impact

- Reflect sessions that hit skip conditions will now escalate after 6 consecutive occurrences
- Dead loops (e.g., context-repository with 18 skips) become visible to the monitoring surface
- Self-monitoring systems properly report stuck states per ADR-0014 (S3-P2 gate)

**Blast radius**: All 8 projects (automatic). No behavioral change to skip logic — only adds counter and escalation after threshold.

## Verification before action (required)

- Read `supervisor/scripts/lib/reflect.sh` around line 76 (the skip path)
- Confirm there is no existing consecutive-skip counter or escalation logic
- Check prior reflections for evidence of silent skip streaks (context-repository, command, others)

## Acceptance criteria

- The skip path checks a consecutive-skip counter file
- After N=6 consecutive skips, a `sourceType: "system"` event is emitted with `eventType: "escalated"`
- The counter resets after escalation
- Each skip logs a visible message to journal (stdout/stderr during reflect.sh run)
- Completion report at `runtime/.handoff/general-supervisor-synthesis-skip-escalation-complete-<iso>.md` referencing this handoff

## Escalation

URGENT if:
- A project is currently in a skip streak >6 and the reflection job hasn't already reported it. If so, emit an URGENT observation to the synthesis queue after landing this change.
- The telemetry event shape conflicts with existing S3-P2 requirements. If so, surface the discrepancy and align.
