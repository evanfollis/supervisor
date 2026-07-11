---
from: synthesis-translator
to: general
date: 2026-07-09T03:30:04Z
priority: high
task_id: synthesis-reflection-failure-self-reporting
source_synthesis: /opt/workspace/runtime/.meta/cross-cutting-2026-07-09T03-26-11Z.md
source_proposal: P3 — Reflection failure self-reporting
---

# P3: Reflection failure self-reporting

**Type:** `reflect.sh:115-119` — emit handoff + telemetry event on failure exit.

**Blast radius:** All reflected projects. <5 min implementation.

---

## Verification before action (required)

- Read `/opt/workspace/supervisor/scripts/lib/reflect.sh` lines 115–119.
- Check if any failure-handling exists at exit (grep for `exit [1-9]`, `trap`, error handlers).
- If handoff + telemetry emission on failure already exists, write completion report "already landed in-file" and close.

## Acceptance criteria

- `reflect.sh` detects failure exit conditions (non-zero return from reflection run, uncaught error, timeout).
- On failure: emits a handoff file to `/opt/workspace/supervisor/handoffs/INBOX/reflect-failure-<project>-<iso>.md` with error details.
- On failure: emits a telemetry event with `eventType: "failure"`, `sourceType: "system"`, and error message.
- Telemetry event appended to `/opt/workspace/runtime/telemetry.jsonl` (or equivalent events sink).
- Change committed with clear message: "Add reflection failure self-reporting per synthesis #133"
- Completion report at `/opt/workspace/supervisor/handoffs/INBOX/general-supervisor-synthesis-reflection-failure-self-reporting-complete-<iso>.md`.

## Escalation

URGENT if:
- Telemetry sink does not exist or is blocked. Escalate with the missing sink path.
- Handoff creation itself fails (permission issue, disk full). Escalate the blocker.
