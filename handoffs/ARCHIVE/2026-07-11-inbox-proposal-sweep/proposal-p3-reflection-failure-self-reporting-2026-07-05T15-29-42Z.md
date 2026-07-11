---
from: synthesis-translator
to: executive
date: 2026-07-05T15:29:42Z
priority: high
task_id: synthesis-p3-reflection-failure-self-reporting
source_synthesis: /opt/workspace/runtime/.meta/cross-cutting-2026-07-05T15-26-01Z.md
source_proposal: "P3 (CARRY — C114, 17th cycle): Reflection failure self-reporting"
---

# P3: Reflection failure self-reporting

**Type:** `reflect.sh:115-119` — emit handoff + telemetry on failure.
**Blast radius:** All reflected projects. <5 min implementation.

## Current state

`reflect.sh` at lines 115-120 checks for output file and emits a warning to stderr if missing:

```bash
if [[ -f "$OUTPUT_FILE" ]]; then
  echo "reflect[$PROJECT]: wrote $OUTPUT_FILE"
else
  echo "reflect[$PROJECT]: WARNING — no output file produced" >&2
  exit 2
fi
```

The script exits but does not emit:
- A handoff file to `/opt/workspace/runtime/.handoff/` (so the executive sees it)
- A telemetry event to `events.jsonl` (so the failure is recorded in the audit trail)

## Proposed change

When `$OUTPUT_FILE` is missing:

1. Emit a handoff file to `/opt/workspace/runtime/.handoff/URGENT-${PROJECT}-reflection-failed.md` with:
   ```markdown
   Reflection session for ${PROJECT} at ${ISO_NOW} did not produce output file.
   Expected: ${OUTPUT_FILE}
   This may indicate a crash, memory limit, or model refusal.
   ```

2. Emit a telemetry event to `/opt/workspace/runtime/.telemetry/events.jsonl`:
   ```json
   {
     "ts": "<iso-timestamp>",
     "project": "${PROJECT}",
     "eventType": "failure",
     "sourceType": "system",
     "component": "reflect",
     "message": "reflection output file not produced",
     "exit_code": 2
   }
   ```

3. Exit with code 2 (unchanged).

## Verification before action (required)

- Read `/opt/workspace/supervisor/scripts/lib/reflect.sh` lines 115-125
- Confirm the current state matches the "Current state" section above
- Check `/opt/workspace/runtime/.handoff/` for any existing `URGENT-*-reflection-failed.md` files — these should not exist (if they do, the failure is not being cleared between cycles)

## Acceptance criteria

- Handoff file emitted when output file is missing
- Telemetry event emitted with correct schema (ts, project, eventType: "failure", sourceType: "system")
- Change committed with message: `reflect: emit handoff + telemetry on failure per synthesis proposal P3`
- Completion report at `runtime/.handoff/general-p3-reflection-failure-complete-<iso>.md`

## Escalation

Low risk. This is a logging enhancement that improves observability without changing control flow.

---

**Background from synthesis (C126):** The reflection loop currently fails silently in ways that don't reach the executive's attention. A failed reflection produces no output file, the script exits 2, and the only signal is a stderr line to the job runner. Handoff + telemetry make the failure visible in the escalation surface and the audit trail. P5-level, carries 13 cycles.
