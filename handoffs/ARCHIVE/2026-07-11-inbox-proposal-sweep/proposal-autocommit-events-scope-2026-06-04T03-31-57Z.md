---
from: synthesis-translator
to: general
date: 2026-06-04T03:31:57Z
priority: high
task_id: synthesis-autocommit-events-scope
source_synthesis: /opt/workspace/runtime/.meta/cross-cutting-2026-06-04T03-27-25Z.md
source_proposal: "P2 — Add `events/` to autocommit scope"
---

# P2 — Add `events/` to autocommit scope (17 cycles open)

**Type:** Shared primitive update — `supervisor-autocommit.sh`

**Action:** Add `events/` to Tier-A dirty-state check (line ~39: add `events/` to the `git status --porcelain -- friction/ handoffs/ system/ ideas/ decisions/` invocation).

**Blast radius:** Supervisor only (automatic). Eliminates the permanent `M events/supervisor-events.jsonl` dirty-tree contributor. Combined with P1, permanently resolves the dirty-tree halt.

**Rationale (from synthesis):** The test artifacts (P1) are not the only dirty-tree contributor. The supervisor-events.jsonl file also remains perpetually modified, blocking the tick. Adding events to autocommit scope removes this structural blocker.

## Verification before action (required)

- Read `/opt/workspace/supervisor/scripts/lib/supervisor-autocommit.sh` around line 39. Verify `events/` is not already in the Tier-A dirty-state check.
- Run `git -C /opt/workspace/supervisor status --porcelain` and confirm `M events/supervisor-events.jsonl` is present (indicating dirty state).
- Check git log to see if this change has already landed in another form.

## Acceptance criteria

- Line ~39 in `supervisor-autocommit.sh` includes `events/` in the `git status --porcelain` command alongside `friction/ handoffs/ system/ ideas/ decisions/`.
- Change committed with message: "Autocommit events/ to supervisor-autocommit scope — removes permanent dirty-tree contributor (C77 synthesis P2)"
- After landing, verify dirty-state check runs without the `M events/supervisor-events.jsonl` line.

## Escalation

URGENT if:
- The `supervisor-autocommit.sh` file does not exist or has a different structure than described.
- The change is already present (in which case write a completion report "already landed at commit <SHA>" and close).
- The events.jsonl file is managed by another system that expects it to remain untracked (surface the conflict).
