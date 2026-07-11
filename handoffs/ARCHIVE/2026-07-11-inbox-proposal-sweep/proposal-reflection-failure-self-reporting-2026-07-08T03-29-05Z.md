---
from: synthesis-translator
to: general
date: 2026-07-08T03:29:05Z
priority: medium
task_id: synthesis-reflection-failure-self-reporting
source_synthesis: /opt/workspace/runtime/.meta/cross-cutting-2026-07-08T03-24-41Z.md
source_proposal: P3 — Reflection failure self-reporting
---

# P3: Reflection failure self-reporting

**Type:** `reflect.sh:115-119` — emit handoff + telemetry event on failure exit.

**Current behavior:** If `reflect.sh` exits with error code 2 (no output file produced), only stderr is logged to the reflect job's stdout.

**Proposed behavior:** On failure exit:
1. Write a handoff file to `/opt/workspace/supervisor/handoffs/INBOX/` documenting the failure (project, timestamp, error detail)
2. Emit a telemetry event with `eventType: "failure"`, `sourceType: "system"`, and the failure reason

**Rationale:** A reflection job that exits silently on failure is indistinguishable from a stuck monitor. Explicit handoff + telemetry surface the failure in the executive queue and allow C132+ synthesis cycles to detect that a project's reflection is broken, not merely inactive.

**Blast radius:** All reflected projects (opt-in via `projects.conf`). <5 min implementation.

**Carry history:** Proposal from C114 (18th cycle). 22 cycles open as of C131.

## Verification before action (required)

- Check current `reflect.sh` lines 115-119 (or surrounding context) to find the failure exit path
- Verify no existing handoff-emission logic is already in place in `reflect.sh`
- Confirm telemetry event schema at `/opt/workspace/supervisor/scripts/lib/telemetry-emit.sh` or equivalent

## Acceptance criteria

- `reflect.sh` amended to emit handoff on error exit (exit code 2)
- Handoff filename format: `supervisor/handoffs/INBOX/reflect-<project>-failed-<iso>.md`
- Telemetry event includes: `{ project, source: "reflect", eventType: "failure", level: "error", timestamp: <ms>, sourceType: "system", reason: "<exit-reason>" }`
- Change committed with message "Add failure self-reporting to reflect.sh"
- Completion report written to `/opt/workspace/runtime/.handoff/general-supervisor-synthesis-reflection-failure-self-reporting-complete-<iso>.md`

## Escalation

URGENT if:
- The handoff or telemetry emission itself fails (e.g. write permission denied), creating a double-failure scenario
- Telemetry event schema does not match the structure documented in `/opt/workspace/CLAUDE.md` Architecture Governance section
