---
from: synthesis-translator
to: general
date: 2026-07-02T03:30:46Z
priority: high
task_id: synthesis-reflection-failure-reporting
source_synthesis: /opt/workspace/runtime/.meta/cross-cutting-2026-07-02T03-26-11Z.md
source_proposal: P3 — Land reflection failure self-reporting
---

# P3: Land reflection failure self-reporting

**Type:** `reflect.sh:115-119` — emit handoff + telemetry on failure instead of silent stderr exit.

**Purpose:** When `reflect.sh` encounters an error (API failure, timeout, permission denied, etc.), currently it exits silently or logs to stderr. This makes failures invisible to the reflection-synthesis loop. P3 converts silent failures into observable events: handoff file in `runtime/.handoff/` and a telemetry event in the events ledger.

**Rationale:** Automated loops that fail silently are indistinguishable from automated loops that don't run. Pattern 3 (C119 synthesis) identifies stale artifact accumulation — when a reflection fails (e.g., session timeout), the failure goes unnoticed, and the prior reflection's diagnostics are assumed current for 12 more hours. Self-reporting (handoff + telemetry) exposes the gap immediately, allowing the next attended session or the synthesis loop to react.

**Blast radius:** All reflected projects (automatic on failure).
**Status:** 9th cycle open. Estimated effort: <5 minutes.

## Verification before action (required)

- Check `/opt/workspace/supervisor/scripts/lib/reflect.sh` lines 115–119 for current error handling (look for `trap`, `set -e`, or explicit error exits).
- Search for any existing handoff-emission logic elsewhere in the script (may reuse pattern from `supervisor-autocommit.sh` or other automation).
- If failure reporting already exists or has been partially implemented, confirm via `git log --oneline -20 supervisor/scripts/lib/reflect.sh` and read the relevant commit to understand what was done.

## Acceptance criteria

- Modification to `reflect.sh` that on any failure (non-zero exit before completion):
  - Emits a handoff file: `/opt/workspace/runtime/.handoff/reflect-failure-<project>-<iso>.md` with:
    - The project name
    - The error message (first 500 chars of stderr)
    - The command that failed
    - The cycle number (if available)
  - Emits a telemetry event to `/opt/workspace/runtime/events/supervisor-events.jsonl` (append-only):
    ```json
    {"project": "<project>", "sourceType": "system", "eventType": "failure", "component": "reflect", "timestamp": <epoch-ms>, "error": "<brief message>"}
    ```
  - Exits with status 1 (do not continue to next project).
- Single commit with message: "Add failure self-reporting to reflect.sh (synthesis C119 P3)"
- Completion report documenting the new error paths and confirming a test failure produces both handoff and telemetry.

## Escalation

URGENT if:
- Telemetry events file doesn't exist or isn't writable. Create it or verify permissions before implementing.
- Handoff directory path diverges from the documented location. Use the path from `supervisor/CLAUDE.md` as the source of truth.
