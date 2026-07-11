---
from: synthesis-translator
to: general
date: 2026-07-02T15:26:24Z
priority: high
task_id: synthesis-reflection-failure-reporting
source_synthesis: /opt/workspace/runtime/.meta/cross-cutting-2026-07-02T15-23-04Z.md
source_proposal: P3 (CARRY — C114, 10th cycle)
---

# P3: Land reflection failure self-reporting

**Type:** `reflect.sh:115-119` — emit handoff + telemetry on failure.

**Context:** This proposal is in the synthesis critical path (item 5 of 6) to unblock the governance automation loop. It completes the reflection failure detection surfacing that prevents silent failures in the per-project reflection sessions.

**Synthesis text:**

> **Type:** `reflect.sh:115-119` — emit handoff + telemetry on failure.
> **Blast radius:** All reflected projects (automatic on failure).
> **Effort:** <5 min.

## Implementation guidance

When the reflection session fails (exit code non-zero from the Claude invocation at reflect.sh:103), emit:

1. A handoff file at `/opt/workspace/runtime/.handoff/URGENT-reflect-${PROJECT}-failure-${ISO_NOW}.md` containing:
   - Project name
   - Timestamp of failure
   - Exit code from claude invocation
   - Tail of stderr from the session if available
   
2. A telemetry event to `events/supervisor-events.jsonl`:
   ```json
   {"ts":"<iso>","agent":"reflect","type":"failure","project":"${PROJECT}","exitCode":<N>,"note":"Reflection session failed for ${PROJECT}"}
   ```

The failure signal prevents silent accumulation of missed reflection cycles and ensures the executive has visibility into which projects have stale reflection state.

## Current implementation reference

The reflect.sh script at lines 115-119 currently shows:
```bash
if [[ -f "$OUTPUT_FILE" ]]; then
  echo "reflect[$PROJECT]: wrote $OUTPUT_FILE"
else
  echo "reflect[$PROJECT]: WARNING — no output file produced" >&2
  exit 2
fi
```

This detects missing output. The enhancement should also emit signals when the Claude invocation itself fails (exit code from line 103).

## Acceptance criteria

- On claude invocation failure (exit >0), emit a named URGENT handoff in `runtime/.handoff/`.
- Emit a telemetry event to `events/supervisor-events.jsonl` with `eventType: "failure"`.
- Handoff is machine-readable (frontmatter + structured body) and includes project name, timestamp, exit code.
- One commit with message: "land reflection failure self-reporting per C120 P3"
- Completion report pointing back to this handoff.

## Escalation

URGENT if:
- Failure detection is already implemented (check for handoff emission or telemetry event in reflect.sh post-claude-invocation).
- The implementation diverges from telemetry event schema (must match `{ts, agent, type, project, exitCode, note}`).
