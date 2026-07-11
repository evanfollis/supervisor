---
from: synthesis-translator
to: general
date: 2026-07-08T03:30:25Z
priority: high
task_id: synthesis-p3-reflection-failure-reporting
source_synthesis: /opt/workspace/runtime/.meta/cross-cutting-2026-07-08T03-24-41Z.md
source_proposal: P3 — Reflection failure self-reporting
---

# P3: Reflection failure self-reporting

**Type:** `reflect.sh:115-119` amendment — emit handoff + telemetry event on failure exit.

**Rationale:** Currently, if the reflection session fails (exits non-zero), the failure is silent and only caught by the absence of an expected output file. Explicit self-reporting would surface failures immediately to the synthesis loop.

**Blast radius:** All reflected projects. <5 min implementation.

---

## Verification before action (required)

- Read `/opt/workspace/supervisor/scripts/lib/reflect.sh` lines 115-119 (the failure check section). Confirm whether failure-reporting logic already exists.
- Check `supervisor-events.jsonl` for recent entries with `type: "reflection_failed"` or similar. If present, the feature may already be implemented.
- If already implemented, write completion report stating "already landed".

## Acceptance criteria

- **New logic after line 119:** If the reflection session exits non-zero or produces no output file:
  - Emit a telemetry event to `$WORKSPACE_TELEMETRY_DIR/events.jsonl` with:
    ```json
    {"ts":"<iso>","project":"<PROJECT>","source":"reflect.sh","eventType":"failure","sourceType":"system","note":"reflection failed for <PROJECT>","exit_code":<code>}
    ```
  - Write a handoff to `/opt/workspace/supervisor/handoffs/INBOX/URGENT-reflection-failed-<PROJECT>-<iso>.md` with the exit code and last few lines of stderr.
- **Escalation to synthesis:** The synthesis job (via `synthesize.sh`) should read these URGENT files and report them in the cross-cutting analysis.
- Commit message: "Add failure self-reporting to reflect.sh (synthesis-p3)".
- Completion report at `/opt/workspace/supervisor/handoffs/INBOX/general-synthesis-p3-failure-reporting-complete-<iso>.md`.

## Non-goals

- No changes to the normal reflection flow or output format.
- Do not change the disallowedTools contract or safety net.
