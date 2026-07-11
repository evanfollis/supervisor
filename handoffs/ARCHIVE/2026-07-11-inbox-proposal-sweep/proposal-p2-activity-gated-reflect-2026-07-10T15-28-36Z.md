---
from: synthesis-translator
to: general
date: 2026-07-10T15:28:36Z
priority: medium
task_id: synthesis-p2-activity-gated-reflect
source_synthesis: /opt/workspace/runtime/.meta/cross-cutting-2026-07-10T15-24-51Z.md
source_proposal: P2 (CARRY — C114, 23rd cycle): Activity-gated reflection for idle projects
---

# P2: Activity-gated reflection for idle projects

**Type:** `reflect.sh` amendment. Skip with carry-forward note when no attended session since last reflection and prior observations are identical.

**Blast radius:** All reflected projects.

## Background

Currently, reflect.sh short-circuits (lines 50-73) if there's been no activity in the last 12h (no commits, telemetry, or JSONL changes). It writes a one-line placeholder to the output file.

The P2 proposal extends this to also carry forward prior observations when they are identical: instead of a bare "no activity" message, emit a copy of the prior reflection marked as a carry-forward so synthesis doesn't see it as a novel observation.

Per Pattern 5 in the synthesis: "This synthesis (C136) contains no new proposals, no new patterns, and no new standing recommendations. The only substantive changes from C135 are counter increments...

The reflection/synthesis loop is running at full diagnostic cadence against a system with zero execution throughput...Running it at 12h cadence against a workspace with 12+ day contact intervals produces ~22 identical reflections per attended session, of which ~1 contains novel signal."

## Verification before action (required)

- Location: `/opt/workspace/supervisor/scripts/lib/reflect.sh` lines 69-73
- Current behavior: writes one-line "Reflection skipped — no activity in window ending..."
- Target behavior: find the most recent prior reflection file for this project; if identical to prior, copy it with a `CARRY-FORWARD` marker instead of running Claude
- Check: `ls -t $META_DIR/${PROJECT}-reflection-*.md | head -2` to get current and prior file

## Implementation notes

1. When short-circuiting at line 69 (no activity), check for a prior reflection file in `$META_DIR`
2. If a prior file exists, compare its content (ignoring timestamps) to the current reflection state if it were run
3. If substantially identical (allow for minor timestamp/counter diffs), write a carry-forward version:
   ```markdown
   # Reflection carry-forward — no activity in window ending <ISO_NOW>
   
   No new activity since last reflection (<PRIOR_ISO>). Prior observations:
   <excerpt or full prior reflection>
   
   **This reflection was not run; the observation above is carried forward.**
   ```
4. If there IS an attended session since last reflection (even with no commits), run normally — carry-forward only applies to pure idle states

## Acceptance criteria

- reflect.sh detects when a reflection would be identical to prior and carries forward instead of spawning Claude
- Carry-forward reflection files are clearly marked so synthesis can filter them
- Change committed with message: "Add carry-forward logic to skip duplicate idle reflections"
- Completion report filed at `runtime/.handoff/general-activity-gated-reflect-complete-<iso>.md`

## Escalation

If determining "identical observation" requires deep content comparison (not just counter diffs), escalate for scope clarification. Consider a simpler heuristic: if no activity AND prior reflection is <24h old, carry forward.
