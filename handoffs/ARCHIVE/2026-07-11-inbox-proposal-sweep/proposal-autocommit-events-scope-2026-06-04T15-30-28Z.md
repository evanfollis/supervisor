---
from: synthesis-translator
to: general
date: 2026-06-04T15:30:28Z
priority: high
task_id: synthesis-autocommit-events-scope
source_synthesis: /opt/workspace/runtime/.meta/cross-cutting-2026-06-04T15-27-05Z.md
source_proposal: P2 — Add `events/` to autocommit scope
---

# Add `events/` to autocommit scope

## Proposal body (from synthesis)

**Type:** Shared primitive update — `supervisor-autocommit.sh` line 55-56 and 61-62.

**Action:** Add `events/` to the `git status --porcelain` check and `git add` invocation.

**Blast radius:** Supervisor only (automatic). Eliminates the permanent `M events/supervisor-events.jsonl` dirty-tree contributor. Combined with P1, permanently resolves the dirty-tree halt.

## Context

The dirty-tree halt (P1 — Remove test artifacts) has blocked all automated project ticks for 312+ hours. While P1 requires principal authorization, P2 is an autonomous primitive update that eliminates one of the two remaining dirty-tree contributors. The synthesis notes this as one of 5 self-applicable proposals that "could be landed by a single attended executive session (~15 min of work, ~10 lines of code across 4 files)." This proposal has been open for **18 cycles** with zero landings.

## Verification before action (required)

- Run `git log --oneline -10 supervisor/scripts/lib/supervisor-autocommit.sh` to verify this change hasn't landed via another path.
- Read the current state of `supervisor/scripts/lib/supervisor-autocommit.sh` at lines 55-62. Confirm that `events/` is not already in the scope.
- If the change is already present, write a completion report stating "already landed" and close.

## Acceptance criteria

- Modify `supervisor/scripts/lib/supervisor-autocommit.sh`:
  - Line 55-56: Add `events/` to the `git status --porcelain` check (alongside existing `handoffs/` scope)
  - Line 61-62: Add `events/` to the `git add` invocation
- Commit with message explaining the synthesis source (imperative mood, explain why not what).
- Verify that the dirty-tree check now includes `events/supervisor-events.jsonl` in the autocommit scope.
- Completion report at `runtime/.handoff/general-synthesis-autocommit-events-scope-complete-<iso>.md` pointing back to this handoff and source synthesis.

## Escalation

URGENT if:
- Primary verification reveals the change is already landed or partially landed. Do not re-apply; write a completion report with the confirmed state.
- The change conflicts with a more recent decision in `supervisor/decisions/`. Do not force-apply; escalate with the conflict named.
