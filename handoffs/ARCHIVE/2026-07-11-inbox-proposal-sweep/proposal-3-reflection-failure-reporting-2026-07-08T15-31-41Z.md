---
from: synthesis-translator
to: general
date: 2026-07-08T15:31:41Z
priority: high
task_id: synthesis-reflection-failure-reporting
source_synthesis: /opt/workspace/runtime/.meta/cross-cutting-2026-07-08T15-25-16Z.md
source_proposal: P3 — Reflection failure self-reporting
---

# P3 — Reflection failure self-reporting

## Proposal

**Type:** `reflect.sh:115-119` — emit handoff + telemetry event on failure exit.

**Current behavior:** If the reflection Claude session fails or produces no output, the script logs a WARNING but does not escalate. The failure is only visible if someone manually checks the reflect.sh log.

**Proposed behavior:** On failure exit (non-zero return from Claude, or missing output file), emit:
1. A handoff to `/opt/workspace/supervisor/handoffs/INBOX/` describing the failure
2. A telemetry event to `/opt/workspace/runtime/friction/events.jsonl` with `eventType: "failure"` and the reflection project name

This ensures reflection failures surface in the automated pressure queue instead of requiring manual log review.

**Blast radius:** All reflected projects. <5 min implementation.

## Verification before action (required)

- Run `git log --oneline -20` on `/opt/workspace/supervisor`. Check if failure self-reporting has already landed via another path.
- Read `/opt/workspace/supervisor/scripts/lib/reflect.sh` around lines 115-119. Check if failure-exit logic is already implemented.
- If either is true, write a completion report stating "already landed" rather than re-applying.

## Acceptance criteria

- `reflect.sh` amended to emit a handoff and telemetry event when the Claude session fails or produces no output.
- Handoff contains: reflection project name, Claude session error (if available), recommend next action (rerun manually, check permissions, etc.).
- Telemetry event shape: `{"ts":"<iso>","source":"reflect.sh","eventType":"failure","project":"<project>","reason":"<error>"}`
- Change committed with clear message explaining the synthesis source.
- Completion report at `/opt/workspace/supervisor/handoffs/INBOX/general-reflection-failure-reporting-complete-<iso>.md` pointing back to this handoff and the source synthesis.

## Escalation

URGENT if:
- Primary verification reveals this has already landed. Write a brief completion report and close.
- The failure-reporting logic itself becomes noisy (emits hundreds of duplicate failures). Revert and escalate with evidence.
