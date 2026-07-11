---
from: synthesis-translator
to: general
date: 2026-07-06T03:28:53Z
priority: high
task_id: synthesis-reflection-failure-self-reporting
source_synthesis: /opt/workspace/runtime/.meta/cross-cutting-2026-07-06T03-24-44Z.md
source_proposal: P3 — Reflection failure self-reporting
---

# Reflection failure self-reporting

## Proposal

**Type:** `reflect.sh:115-119` — emit handoff + telemetry event on failure exit.

**Blast radius:** All reflected projects. <5 min implementation.

**Context:** When reflect.sh encounters an error and exits, it should emit a self-report so the failure is visible in the escalation system, not silent.

## Verification before action (required)

- Check `/opt/workspace/supervisor/scripts/lib/reflect.sh` around lines 115–119 for existing error handling.
- Look for patterns like `trap` cleanup or error-exit paths that already emit telemetry.
- If failure self-reporting is already implemented, verify it emits both:
  - A handoff file to `runtime/.handoff/` with escalation detail
  - A telemetry event with proper `sourceType` and `eventType: "failure"`
- If already implemented, write completion report stating "already landed and verified".

## Acceptance criteria

If not already landed:
- `reflect.sh` error-exit paths (e.g., `set -e` failure, explicit `exit` on error) emit a telemetry event with:
  - `eventType: "failure"`
  - `sourceType: "system"` (it's an automated process)
  - Reason/stderr captured in event or linked file
- Write a handoff file to `/opt/workspace/runtime/.handoff/<project>-reflection-failed-<iso>.md` with:
  - Project name
  - Failure reason (stderr output or error description)
  - Suggested next steps
- Commit message: "Add self-reporting to reflect.sh failure paths — emit handoff + telemetry on exit"
- Completion report at `runtime/.handoff/general-complete-reflection-failure-self-reporting-<iso>.md`

## Escalation

If the failure paths already exist but don't emit reports, escalate with the specific error paths that need instrumentation.
