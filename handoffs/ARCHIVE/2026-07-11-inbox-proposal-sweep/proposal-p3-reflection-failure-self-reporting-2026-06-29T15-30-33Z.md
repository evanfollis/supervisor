---
from: synthesis-translator
to: executive
date: 2026-06-29T15:30:33Z
priority: high
task_id: synthesis-p3-reflection-failure-self-reporting
source_synthesis: /opt/workspace/runtime/.meta/cross-cutting-2026-06-29T15-27-11Z.md
source_proposal: P3 (CARRY) — Land P7 — reflection failure self-reporting
---

# P3 (CARRY): Land P7 — reflection failure self-reporting

**Status:** 4th carry-forward cycle. `reflect.sh:115-119` still exits with code 2 and stderr only. No handoff written, no telemetry event emitted. Independent of all other proposals. <5 min effort. The 7-day blind period (C112 Pattern 6) demonstrated the failure class this prevents.

**Current behavior at reflect.sh:115-119:**
```bash
if [[ -f "$OUTPUT_FILE" ]]; then
  echo "reflect[$PROJECT]: wrote $OUTPUT_FILE"
else
  echo "reflect[$PROJECT]: WARNING — no output file produced" >&2
  exit 2
fi
```

**Required addition:** When the reflection fails to produce output (exit 2 case), emit a telemetry event to `supervisor/events/supervisor-events.jsonl` with:
- `ts`: ISO 8601 timestamp
- `agent`: "reflect"
- `type`: "failure"
- `ref`: "reflect.sh"
- `note`: one-line describing the failure (e.g., "reflection for {PROJECT} failed to produce output file")

This ensures:
1. Reflection failures are visible in telemetry, not silent.
2. The supervisor tick or synthesis job can detect and report on reflection failure patterns.
3. A 7-day silent reflection failure (as happened in C112) becomes visible to the executive.

**Blast radius:** All reflected projects (automatic — fires on failure).

## Verification before action (required)

- Run `git log --oneline -5` on `/opt/workspace/supervisor/` and check if this event emission has already landed via another path.
- Read `supervisor/scripts/lib/reflect.sh` lines 115-119. Check if telemetry event emission code is already present.
- If already present, write a completion report stating "already landed at commit <SHA>" rather than re-applying.

## Acceptance criteria

- `reflect.sh` emits a telemetry event (type: "failure") to `supervisor/events/supervisor-events.jsonl` when the reflection session fails to produce output.
- Event minimum fields: `ts`, `agent`, `type`, `ref`, `note`. Minimum shape: `{"ts":"<iso>","agent":"reflect","type":"failure","ref":"reflect.sh","note":"<one-line>"}`.
- Change committed with clear message explaining the synthesis source and the failure detection purpose.
- Completion report at `runtime/.handoff/general-supervisor-synthesis-p3-complete-<iso>.md` pointing back to this handoff and the source synthesis.

## Escalation

URGENT if:
- The telemetry event format differs from the supervisory standard described in `/opt/workspace/CLAUDE.md` (Architecture Governance section). Check the standard before committing.
- The event destination path is wrong or the file is not writable. Verify `supervisor/events/` exists and autocommit can write there.
