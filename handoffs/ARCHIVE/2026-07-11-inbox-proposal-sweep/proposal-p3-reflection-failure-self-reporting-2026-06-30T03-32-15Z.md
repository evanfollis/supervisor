---
from: synthesis-translator
to: general
date: 2026-06-30T03:32:15Z
priority: high
task_id: synthesis-p3-reflection-failure
source_synthesis: /opt/workspace/runtime/.meta/cross-cutting-2026-06-29T15-27-11Z.md
source_proposal: P3 - Land reflection failure self-reporting
---

# P3: Reflection failure self-reporting in reflect.sh

## Full Proposal (from C114)

**Status in C114:** 4th cycle carry-forward. Independent of all other proposals. <5 min effort. The 7-day blind period (C112 Pattern 6) demonstrated the failure class this prevents.

**Current behavior (in `/opt/workspace/supervisor/scripts/lib/reflect.sh` lines 115-119):**
```bash
if [[ -f "$OUTPUT_FILE" ]]; then
  echo "reflect[$PROJECT]: wrote $OUTPUT_FILE"
else
  echo "reflect[$PROJECT]: WARNING — no output file produced" >&2
  exit 2
fi
```

**Issue:** When reflection fails (exit code 2), the script exits with stderr only. No telemetry event is emitted. No log entry in the workspace telemetry system. The failure is invisible to meta-monitoring.

**Proposed fix:** Emit a telemetry event when reflection fails. This allows the meta-loop and executive to detect and respond to reflection failures. The 7-day blind period in C112 demonstrated that silent reflection failures can accumulate for a week before being noticed.

**Blast radius:** All reflected projects (automatic — fires on failure).

**Effort:** Independent of P2/P1/P4. <5 minutes. No dependencies.

## Verification before action (required)

- Run `git log --oneline -20` on `/opt/workspace`. Check if this failure self-reporting has already landed via another path (commit message would reference P3, failure reporting, or reflection telemetry).
- Read `/opt/workspace/supervisor/scripts/lib/reflect.sh` lines 115-125 (failure block). Verify that it does NOT yet emit a telemetry event on failure (grep for `emit_event` or telemetry call in that block).
- If the telemetry emission is already present, write a completion report stating "already landed" and close.

## Acceptance criteria

- When reflection fails (output file not created), the script emits a telemetry event before exiting with code 2
- Event shape: follows the pattern in `supervisor/scripts/lib/supervisor-autocommit.sh` or `reflect.sh` itself (e.g. `emit_event "reflection_failure" "project=$PROJECT reason=no_output_file"`)
- The event includes:
  - `project`: the project name
  - `reason`: why the reflection failed (e.g., "no output file", "claude session error")
- Change committed with message: "Add telemetry event for reflection failures — enable detection of silent failures" (or similar — explain the why)
- Completion report at `/opt/workspace/supervisor/handoffs/INBOX/general-p3-reflection-failure-complete-<iso>.md` pointing back to this handoff and the source synthesis

## Escalation

URGENT if:
- Primary verification reveals this telemetry emission is already landed. Write "obsolete — already landed" and close.
- The `emit_event` function is not available in the reflect.sh environment. Escalate with evidence of where emit_event is defined and how it should be called from reflect.sh.
- The failure case (lines 115-119) has been restructured so substantially that the proposed location no longer applies. Escalate with the current structure of that block.
