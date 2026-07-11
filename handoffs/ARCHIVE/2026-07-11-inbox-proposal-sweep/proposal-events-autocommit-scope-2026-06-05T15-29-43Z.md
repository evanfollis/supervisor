---
from: synthesis-translator
to: general
date: 2026-06-05T15:29:43Z
priority: critical
task_id: synthesis-events-autocommit-scope
source_synthesis: /opt/workspace/runtime/.meta/cross-cutting-2026-06-05T15-26-05Z.md
source_proposal: P2 — Add `events/` to autocommit scope (20 cycles open)
---

# P2 — Add `events/` to autocommit scope

**Type:** Shared primitive update — `supervisor-autocommit.sh`.

**Pattern:** The entire automated governance stack has been halted for ~360h (15 days) by two untracked 0-byte test files. The immediate fix is P1 (git clean), but this becomes a permanent problem if `events/` is not added to the autocommit scope in `supervisor-autocommit.sh`.

The dirty-tree check blocks the tick whenever the working tree has modifications. Currently, `events/supervisor-events.jsonl` is not in the autocommit scope, so telemetry emissions (which append to this file) cause the dirty-tree halt to trigger repeatedly.

**Failure class:** Safety net (dirty-tree check) with insufficient allowlist for operational state files.

**Proposed change:**
Update `supervisor-autocommit.sh` to include `events/` directory in the autocommit scope, so that telemetry events appended to `events/supervisor-events.jsonl` do not cause the tick to halt.

**Blast radius:** Supervisor only (automatic). Combined with P1 (removing the test artifacts), this permanently resolves the dirty-tree halt and prevents recurrence.

**Evidence:** Cycle 20 (Observations #1): "Test artifacts Day 14. Halt root cause." Cycle 19 (Observations #1): "P1 still the single critical unblock." Verified live: `git status --short` confirms `M events/supervisor-events.jsonl` as a persistent dirty-tree contributor.

## Verification before action (required)

- Read `/opt/workspace/supervisor/scripts/lib/supervisor-autocommit.sh` to understand the current autocommit pattern
- Identify the section where autocommit paths are defined
- Verify this change has not already landed (check recent commits)
- If already landed, write completion report noting "already landed at commit <SHA>" and exit

## Acceptance criteria

- `events/` directory is added to the autocommit scope in `supervisor-autocommit.sh`
- The change ensures telemetry emissions to `events/supervisor-events.jsonl` do not trigger dirty-tree halts
- Commit message explains the synthesis source and why this prevents the class of dirty-tree failures
- Completion report at `/opt/workspace/runtime/.handoff/general-synthesis-events-autocommit-complete-<iso>.md` pointing back to this handoff and source synthesis

## Escalation

URGENT if:
- Verification reveals this change has already landed by another path — write brief completion saying "obsolete — already landed" and close
- The autocommit.sh structure has changed significantly since C80 synthesis — surface the structural mismatch
- This change requires coordination with P1 (test artifact removal) for full effectiveness — note the dependency in the completion report
