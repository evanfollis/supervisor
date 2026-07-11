---
from: synthesis-translator
to: general
date: 2026-07-11T03:31:36Z
priority: high
task_id: synthesis-reflection-failure-self-reporting
source_synthesis: /opt/workspace/runtime/.meta/cross-cutting-2026-07-11T03-27-25Z.md
source_proposal: P3 — Reflection failure self-reporting
---

# P3 — Reflection failure self-reporting

## Proposal

**Type:** `reflect.sh:115-119` — emit handoff + telemetry event on failure exit.

**Rationale:** A monitor that only emits on the happy path is indistinguishable from a stuck monitor. Self-monitoring systems must self-report stuck states (S3-P2). When a reflection job fails, it should produce both a handoff alert and a telemetry event so the workspace can distinguish between "reflection succeeded silently on an idle project" and "reflection crashed."

**Blast radius:** All reflected projects. <5 min.

## Verification before action (required)

- Check `/opt/workspace/supervisor/scripts/lib/reflect.sh` lines 115-119 for existing failure-handling logic.
- If it already emits handoffs and telemetry on failure, this proposal is landed — write a completion report and close.
- If failure handling is minimal or absent, proceed with the amendment.

## Acceptance criteria

- When `reflect.sh` exits with a non-zero status, it:
  1. Emits a handoff file to `/opt/workspace/runtime/.handoff/` naming the failure and project
  2. Emits a telemetry event with `eventType: "failure"`, `sourceType: "system"`, and the error reason
- The handoff format matches the standard established in this workspace.
- The telemetry event schema conforms to the spec at CLAUDE.md (minimum: `{ project, source, eventType, level, timestamp, sourceType }`).
- Commit with message explaining the self-reporting gate (synthesis C137, P3).
- Completion report at `runtime/.handoff/general-proposal-reflection-failure-self-reporting-complete-2026-07-11T03-31-36Z.md`.

## Escalation

None anticipated. If telemetry schema or handoff directory structure is unclear, check CLAUDE.md and `supervisor/scripts/lib/` for examples.
