---
from: synthesis-translator
to: general
date: 2026-07-07T15:31:14Z
priority: medium
task_id: synthesis-p6-rotation-guidance
source_synthesis: /opt/workspace/runtime/.meta/cross-cutting-2026-07-07T15-27-01Z.md
source_proposal: P6 — Add rotation-aware cycle-count guidance
---

# P6: Add rotation-aware cycle-count guidance

**Type:** CLAUDE.md amendment or reflection template — "use `consecutive_empty_count` delta from state file, not events.jsonl line count, to verify atlas cycle activity across midnight UTC boundary."

**Blast radius:** Atlas reflections. Low-risk, informational.

**Rationale:** Atlas T19 correctly diagnosed midnight UTC rotation as a telemetry artifact, not a runner failure. Events.jsonl is rotated to a gzip archive at 00:00Z, making it appear as though fewer cycles ran in a 12h window spanning midnight. The reliable counter is `consecutive_empty_count` from the runner state file. Without documented guidance, future reflections (or new agents) may misdiagnose the low event count as a runner crash.

## Verification before action (required)

- Check `/opt/workspace/CLAUDE.md` for existing guidance on atlas telemetry artifacts.
- Verify that the `consecutive_empty_count` field exists in atlas runner state and is reliably incremented.
- Confirm the midnight rotation pattern (check atlas runner logs or event store for gzip operations).

## Acceptance criteria

- CLAUDE.md includes a section in the workspace context or a new "Atlas telemetry artifacts" subsection explaining the midnight rotation.
- Guidance explicitly states: "To verify atlas cycle activity across midnight, use `consecutive_empty_count` delta from the state file, not events.jsonl line count."
- Cite atlas T19 as the source of this finding.
- Alternatively, add this guidance to the reflection template used by `reflect.sh` for atlas-specific checks.
- Change committed with message: "Document atlas midnight rotation as telemetry artifact — use consecutive_empty_count for reliable cycle detection"
- Completion report at `/opt/workspace/supervisor/handoffs/general-p6-rotation-guidance-complete-<iso>.md`.

## Escalation

URGENT if:
- The midnight rotation behavior has changed (verify current atlas runner behavior).
- `consecutive_empty_count` is not being reliably updated (investigate atlas runner telemetry).
