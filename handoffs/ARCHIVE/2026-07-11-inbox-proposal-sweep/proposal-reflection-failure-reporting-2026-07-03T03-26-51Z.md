---
from: synthesis-translator
to: general
date: 2026-07-03T03:26:51Z
priority: high
task_id: synthesis-reflection-failure-reporting
source_synthesis: /opt/workspace/runtime/.meta/cross-cutting-2026-07-03T03-23-57Z.md
source_proposal: P3 (CARRY — C114, 11th cycle): Land reflection failure self-reporting
---

# P3: Land reflection failure self-reporting

Type: `reflect.sh` script enhancement — emit handoff + telemetry on failure.

Location: `/opt/workspace/supervisor/scripts/lib/reflect.sh:115-119`

Current behavior (lines 118–119):
```bash
else
  echo "reflect[$PROJECT]: WARNING — no output file produced" >&2
  exit 2
fi
```

Required enhancement:
When reflect.sh fails to produce output (line 118), before exiting:
1. Emit a telemetry event to `supervisor-events.jsonl` with `type: "failure"`, `detail: "reflect_no_output"`, `project: "$PROJECT"`, `sourceType: "system"`
2. Write a handoff file to `/opt/workspace/runtime/.handoff/reflect-failure-<project>-<iso>.md` documenting the failure
3. Then exit with code 2

Rationale from C121: Reflect.sh is part of the governance automation. When it fails silently, the synthesis loop loses the project's reflection input for that cycle. The automation should self-report this state instead of just logging a warning. This enables the synthesis job to detect and escalate reflect failures without manual monitoring.

Effort: <5 minutes

Blast radius: All reflected projects with optional opt-in via `projects.conf`.

## Verification before action (required)

- Read `/opt/workspace/supervisor/scripts/lib/reflect.sh` lines 115–125 to confirm current state
- Verify that lines 118–119 contain only the warning and exit, with no subsequent handoff/telemetry code

## Acceptance criteria

- Lines 118–119 are enhanced to:
  - Call `emit_event` to record failure to telemetry (use existing `emit_event` function pattern from supervisor-autocommit.sh as reference)
  - Write handoff file with minimal structure: project, failure reason, timestamp
  - Then exit with code 2 as before
- Script is tested to verify events.jsonl receives the event and handoff file is written
- Commit with message: "Add failure self-reporting to reflect.sh (synthesis C121)"
- Completion report at `runtime/.handoff/general-proposal-reflection-failure-reporting-complete-<iso>.md`

## Escalation

URGENT if:
- The enhancement is already in place (use completion report "already landed" path)
- `emit_event` function is not available in reflect.sh's context (check supervisor-autocommit.sh for the pattern)
