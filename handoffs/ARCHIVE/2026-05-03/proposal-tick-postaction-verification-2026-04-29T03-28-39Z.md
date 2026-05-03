---
from: synthesis-translator
to: general
date: 2026-04-29T03:28:39Z
priority: high
task_id: synthesis-tick-postaction-verification
source_synthesis: /opt/workspace/runtime/.meta/cross-cutting-2026-04-29T03-24-29Z.md
source_proposal: Proposal 1 — Shared primitive post-action state verification in tick wrapper
---

# Shared primitive — post-action state verification in tick wrapper

## Problem

Three independent verification failures in supervisor automation share one root cause: systems report success based on having performed an action, without verifying the action produced the expected state. Specific manifestations:

1. **Tick claims materialized/created files on main, but they are not present.** Tick emits success event at write time, not at post-merge verification time. This is the 10th+ consecutive cycle.

2. **Tick event labeling inaccuracy.** Two consecutive model invocation failures (16:49Z, 18:48Z Apr 28) emitted `session_reflected` events with failure notes, but no `escalated` event fired despite the S3-P2 rule (N consecutive same-reason failures → `escalated`). The wrapper commits the branch and emits a success-shaped event, but does not track consecutive failure state.

3. **Synthesis-translator missing `synthesis_reviewed` event.** The prior synthesis (15:28Z) was substantively processed, but no `synthesis_reviewed` event appears in the event stream. The charter event model requires this event.

## Solution sketch

Verify postconditions before emitting success-class events:

**A. Post-merge file verification** (in supervisor-tick.sh after branch merge to main):
```bash
# After tick branch merge to main, before emitting session_reflected:
for claimed_file in $(grep -E 'materialized|created' "$TICK_REPORT"); do
  [ -f "$claimed_file" ] || emit_escalated "ghost-write: $claimed_file claimed but absent on main"
done
```

**B. Consecutive-failure tracking** (tick invocation wrapper):
```bash
# At tick invocation point:
FAIL_COUNT_FILE="$RUNTIME/.meta/tick-consecutive-failures"
count=$(cat "$FAIL_COUNT_FILE" 2>/dev/null || echo 0)
if [ "$exit_code" -ne 0 ]; then
  echo $((count + 1)) > "$FAIL_COUNT_FILE"
  [ $((count + 1)) -ge 2 ] && emit_escalated "tick-invocation-failure" "consecutive=$((count+1))"
else
  echo 0 > "$FAIL_COUNT_FILE"
fi
```

**C. Synthesis-translator `synthesis_reviewed` emission** (in synthesis-translator):
Ensure that after successfully processing proposals, a `synthesis_reviewed` event is emitted with the synthesis file reference.

## Acceptance criteria

- Post-action file verification gate is implemented in `supervisor-tick.sh`; ticket-claimed files are validated to exist on main before success event
- Consecutive-failure tracking is implemented; escalation fires on threshold breach per S3-P2 rule
- Synthesis-translator emits `synthesis_reviewed` event after processing complete
- Changes committed with messages explaining the synthesis source and Pattern 2 context
- Verification: rerun the next supervisor tick and confirm that false-positive "materialized" claims now trigger escalation events

## Escalation

URGENT if the prior tick already claimed success for a file that is not actually present — this proposal is fixing a recurring false-positive that will recur each tick until landed.

## Notes

- Blast radius: Supervisor project only (tick wrapper + synthesis tooling)
- Automatic: runs on every tick; does not change execution paths
- Low risk: adds verification without changing success/failure semantics
- Cite: supervisor-reflection-2026-04-29T02-26-03Z §Observations #1–3
