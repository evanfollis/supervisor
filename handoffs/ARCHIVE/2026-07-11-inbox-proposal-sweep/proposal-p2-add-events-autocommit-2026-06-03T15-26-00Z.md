---
from: synthesis-translator
to: general
date: 2026-06-03T15:26:00Z
priority: high
task_id: synthesis-p2-events-autocommit
source_synthesis: /opt/workspace/runtime/.meta/cross-cutting-2026-06-03T15-23-08Z.md
source_proposal: P2 — Add `events/` to autocommit scope (16 cycles open)
---

# P2 — Add `events/` to autocommit scope

**Type:** Shared primitive update — `supervisor-autocommit.sh`.

**Sketch:** Add `events/supervisor-events.jsonl` to Tier-A autocommit paths.

**Blast radius:** Supervisor only (automatic). Eliminates the `M events/supervisor-events.jsonl` dirty-tree contributor. Combined with P1, permanently resolves the dirty-tree halt condition.

**Rationale:** The automated stack has been halted for 11 days due to dirty-tree checks. One of the two untracked test artifacts can be resolved via P1 (manual `git clean`), but `events/supervisor-events.jsonl` gets modified during normal telemetry operations. By adding this file to the autocommit scope, we eliminate one dirty-tree contributor permanently.

## Verification before action (required)

- Read `/opt/workspace/supervisor/scripts/lib/supervisor-autocommit.sh` and check if `events/supervisor-events.jsonl` is already in Tier-A autocommit paths.
- If already present, write a completion report stating "already present in supervisor-autocommit.sh" rather than re-applying.

## Acceptance criteria

- `events/supervisor-events.jsonl` is added to the Tier-A autocommit section of `supervisor-autocommit.sh`.
- Change committed with message: "Add events/supervisor-events.jsonl to autocommit scope; eliminates dirty-tree contributor (synthesis P2)"
- No additional review needed — straightforward configuration change.
- Completion report at `runtime/.handoff/general-supervisor-synthesis-p2-complete-<iso>.md` pointing back to this handoff and the source synthesis.

## Escalation

URGENT if:
- The file is already present — verify in-file and close.
- The change causes any test or integration issues during next supervisor tick — report and defer pending investigation.
