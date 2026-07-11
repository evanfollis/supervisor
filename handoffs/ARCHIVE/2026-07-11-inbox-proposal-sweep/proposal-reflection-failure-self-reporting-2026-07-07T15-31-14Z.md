---
from: synthesis-translator
to: general
date: 2026-07-07T15:31:14Z
priority: high
task_id: synthesis-p3-failure-self-report
source_synthesis: /opt/workspace/runtime/.meta/cross-cutting-2026-07-07T15-27-01Z.md
source_proposal: P3 — Reflection failure self-reporting
---

# P3: Reflection failure self-reporting

**Type:** `reflect.sh:115-119` — emit handoff + telemetry event on failure exit.

**Blast radius:** All reflected projects. <5 min implementation.

**Rationale:** Per governance rules (ADR-0027, S3-P2), self-monitoring systems must self-report stuck states. A reflection that fails silently is indistinguishable from a stuck monitor. This closes that gap: reflect.sh aborts with a handoff + telemetry event if the reflection process itself crashes or exits non-zero.

## Verification before action (required)

- Check `supervisor/scripts/lib/reflect.sh` lines 115-119. Verify current failure-exit behavior.
- Check whether telemetry event schema already supports reflection failure events.

## Acceptance criteria

- When `reflect.sh` exits with error status, it emits a telemetry event with `eventType: "failure"` and `sourceType: "system"`.
- It deposits a handoff at `/opt/workspace/supervisor/handoffs/INBOX/reflect-failure-<project>-<iso>.md` naming the project and error.
- Change committed with message: "Add reflection failure self-reporting per S3-P2 — emit telemetry + handoff on exit error"
- Completion report at `/opt/workspace/supervisor/handoffs/general-p3-failure-self-report-complete-<iso>.md`.

## Escalation

URGENT if:
- The telemetry event schema does not support reflection-failure events (extend the schema; this is not a blocker).
- Failure events are not reaching the telemetry store (verify event sink is writable).
