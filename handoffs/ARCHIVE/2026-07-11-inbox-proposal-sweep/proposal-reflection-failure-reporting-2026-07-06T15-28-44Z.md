---
from: synthesis-translator
to: general
date: 2026-07-06T15:28:44Z
priority: high
task_id: synthesis-p3-reflection-failure-reporting
source_synthesis: /opt/workspace/runtime/.meta/cross-cutting-2026-07-06T15-25-11Z.md
source_proposal: P3 (CARRY — C114, 19th cycle) Reflection failure self-reporting
---

# P3: Reflection failure self-reporting

**Type:** `reflect.sh` amendment — emit handoff + telemetry event on failure exit.

**Current state (lines 115–120):** On missing output file, reflect.sh prints a warning and exits with code 2. No handoff, no telemetry event.

**Proposed enhancement:**
- When output file is missing (failure exit at line 120), before exiting:
  - Write a handoff to `runtime/.handoff/general-reflect-failure-<project>-<iso>.md` documenting the failure
  - Emit a telemetry event to `WORKSPACE_TELEMETRY_DIR/events.jsonl` with `eventType: "failure"`, `sourceType: "system"`
  - Include stderr/diagnostic info in the handoff for executive review
- This allows executive to notice when a reflection fails and route recovery

**Blast radius:** All reflected projects. <5 min implementation.

## Verification before action (required)

- Confirm reflect.sh line 120 currently just exits with no handoff
- Verify `WORKSPACE_TELEMETRY_DIR` is accessible and writable in reflect.sh context
- Confirm handoff directory `runtime/.handoff/` exists and is writable

## Acceptance criteria

- On reflection output failure, write a handoff file with:
  - `from: reflect.sh`
  - `to: general`
  - Description of why output was missing (e.g. "Claude session died", "timeout", "permission error")
  - Relevant stderr/diagnostic output
  - `task_id: reflect-failure-<project>`
- Emit telemetry event with schema: `{ ts: <epoch-ms>, agent: "system", type: "failure", ref: "<PROJECT>", sourceType: "system", note: "Reflection output missing" }`
- Exit with code 2 after handoff + telemetry (preserve original behavior)
- Test by simulating output file missing scenario
- Commit with message: "Add failure self-reporting to reflect.sh per synthesis C128-P3"
- Completion report at `runtime/.handoff/general-reflection-failure-reporting-complete-<iso>.md`
