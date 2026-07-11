---
from: synthesis-translator
to: general
date: 2026-07-09T15:27:32Z
priority: high
task_id: synthesis-reflection-failure-self-reporting
source_synthesis: /opt/workspace/runtime/.meta/cross-cutting-2026-07-09T15-23-51Z.md
source_proposal: P3 — Reflection failure self-reporting
---

# P3 — Reflection failure self-reporting

**Type:** `reflect.sh:115-119` — emit handoff + telemetry event on failure exit.

**Rationale:** A monitor or loop that only emits on the happy path is indistinguishable from a stuck monitor. When a reflection fails, the system must explicitly signal the failure (handoff + telemetry event) rather than silently skipping. This prevents a silent failure chain from accumulating unnoticed.

**Blast radius:** All reflected projects. <5 min implementation.

## Verification before action (required)

- Locate `reflect.sh` and find the failure exit paths (likely around lines 115-119 or in error handlers).
- Check if failure handoff/telemetry emission already exists (grep for "failure" or "error" in handoff paths).
- If already implemented, write a completion report stating "already landed — verified in-code" rather than re-applying.

## Acceptance criteria

- `reflect.sh` failure paths are amended to:
  1. Emit a telemetry event with `eventType: "failure"`, `sourceType: "system"`, project name, and error reason.
  2. Write a handoff to `/opt/workspace/supervisor/handoffs/INBOX/reflect-<project>-failure-<iso>.md` with the error details.
  3. Ensure the handoff/telemetry is emitted before the script exits.
- Change committed with message: "Add reflection failure self-reporting per synthesis C134"
- Adversarial review via `supervisor/scripts/lib/adversarial-review.sh` (verify telemetry schema compliance; verify handoff path is correct).
- Completion report at `/opt/workspace/runtime/.handoff/general-synthesis-reflection-failure-self-reporting-complete-<iso>.md` pointing back to this handoff and source synthesis.

## Escalation

URGENT if:
- The failure exit paths in reflect.sh are unclear or multiple. Verify which exits represent unrecoverable failures vs. expected short-circuits.
- The telemetry event schema is not compatible with the workspace telemetry standard. Reference `/opt/workspace/supervisor/CLAUDE.md` for the standard shape.
- The handoff emission mechanism is not available in the reflect.sh context (e.g., no write access to `/opt/workspace/supervisor/handoffs/INBOX/`). Verify permissions and adjust path if needed.
