---
from: synthesis-translator
to: general
date: 2026-07-05T03:33:26Z
priority: high
task_id: synthesis-reflect-failure-self-report
source_synthesis: /opt/workspace/runtime/.meta/cross-cutting-2026-07-05T03-28-11Z.md
source_proposal: P3 (CARRY — C114, 16th cycle): Reflection failure self-reporting
---

# P3: Reflection failure self-reporting

**Type:** `reflect.sh:115-119` — add handoff + telemetry emission on session failure.

**Blast radius:** All reflected projects (per `projects.conf` opt-in). ~5 min implementation. **16th cycle open — recurring across 16 synthesis cycles since C110.**

## Current behavior (lines 115–119)

The script checks if the reflection output file was created:

```bash
if [[ -f "$OUTPUT_FILE" ]]; then
  echo "reflect[$PROJECT]: wrote $OUTPUT_FILE"
else
  echo "reflect[$PROJECT]: WARNING — no output file produced" >&2
  exit 2
fi
```

When the reflection session fails to produce output, the script exits with code 2 but does NOT:
- Write a handoff to notify the executive
- Emit telemetry documenting the failure
- Provide context about why the session failed

## Proposed behavior

Add after line 119 (before the `resolve_claim_path()` function definition):

```bash
else
  # Reflection session failed to produce output. Handoff to executive.
  FAILURE_HANDOFF="$WORKSPACE_HANDOFF_DIR/URGENT-${PROJECT}-reflection-failed-${ISO_NOW}.md"
  cat > "$FAILURE_HANDOFF" <<EOF
---
from: reflect.sh
project: ${PROJECT}
timestamp: ${ISO_NOW}
severity: URGENT
---

# Reflection session failed

Reflection run for **${PROJECT}** at ${ISO_NOW} did not produce output.
Expected file: \`${OUTPUT_FILE}\`

Session invocation may have crashed, timed out, or been blocked.
Next reflection cycle will re-attempt automatically.

## Debug notes

- Project dir: \`${PROJECT_DIR}\`
- Workspace session dir: \`${SESSION_DIR}\`
- Output file was not created: \`${OUTPUT_FILE}\`
- Exit code: 2
EOF

  # Telemetry event.
  if [[ -w "$WORKSPACE_TELEMETRY_DIR/events.jsonl" ]]; then
    echo "{\"ts\":\"${ISO_NOW}\",\"agent\":\"system\",\"project\":\"${PROJECT}\",\"sourceType\":\"system\",\"eventType\":\"failure\",\"level\":3,\"type\":\"reflection_failure\",\"ref\":\"${FAILURE_HANDOFF}\",\"note\":\"Reflection session did not produce output\"}" >> "$WORKSPACE_TELEMETRY_DIR/events.jsonl"
  fi

  echo "reflect[$PROJECT]: FAILURE — wrote $FAILURE_HANDOFF" >&2
  exit 2
fi
```

**Rationale (from synthesis C125):**
- **Pattern:** A system that only emits on success is indistinguishable from a stuck system (per ADR-0013, S3-P2 discipline).
- **Current problem:** Reflection failures (crashed sessions, timeouts, tool blockages) are silent — they don't surface to the executive unless the next cycle's synthesis notices the reflection is missing.
- **Impact:** The 16-cycle carry-forward shows reflection failures are recurring but invisible. By the time they're noticed, the delay has widened the window they're supposed to diagnose.
- **Narrowest fix:** Emit a handoff + telemetry event immediately when a reflection session fails. The executive sees it on reentry; meta-scan catches patterns.

## Verification before action (required)

- Read `/opt/workspace/supervisor/scripts/lib/reflect.sh` lines 115–119. Confirm this code is present and has NOT been amended with failure handling.
- Check `/opt/workspace/supervisor/decisions/` for any prior decision on reflection failure handling. None found.
- Confirm telemetry dir structure exists: `/opt/workspace/runtime/.telemetry/` (or update the event path if the actual location differs).

## Acceptance criteria

- Lines 115–119 of `reflect.sh` are amended with the failure handoff + telemetry emission
- Change committed with message: "Add reflection session failure self-reporting per synthesis C125 (C114, 16th carry-forward)"
- No adversarial review needed (mechanical addition following established telemetry pattern)
- Verify: run a test reflection on a project with a synthetic failure (e.g. set `PROJECT_DIR` to a nonexistent path) and confirm a URGENT-*-reflection-failed handoff is created and telemetry event is emitted

## Escalation

None anticipated. This is mechanical implementation of the standing S3-P2 discipline ("Self-monitoring systems must self-report stuck states").

