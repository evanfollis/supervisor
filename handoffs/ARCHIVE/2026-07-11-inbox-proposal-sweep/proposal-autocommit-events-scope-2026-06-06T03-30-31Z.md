---
from: synthesis-translator
to: general
date: 2026-06-06T03:30:31Z
priority: high
task_id: synthesis-autocommit-events-scope
source_synthesis: /opt/workspace/runtime/.meta/cross-cutting-2026-06-06T03-25-20Z.md
source_proposal: "P2 — Add `events/` to autocommit scope (21 cycles open)"
---

# P2 — Add `events/` to autocommit scope

**Type:** Shared primitive update — `supervisor-autocommit.sh`.

**Blast radius:** Supervisor only (automatic). Combined with P1 (principal to remove test artifacts), permanently resolves the dirty-tree halt class by ensuring `events/supervisor-events.jsonl` changes are auto-committed.

**Context:** Cycle 21 verified dirty-tree state shows:
```
 M events/supervisor-events.jsonl
?? scripts/lib/.erofs-test-meta-reflection
?? scripts/lib/TEST_WRITE_2951547
```

The autocommit scope currently excludes `events/`, causing the dirty-tree check to block the tick every cycle. Adding `events/supervisor-events.jsonl` to autocommit scope in `supervisor-autocommit.sh` ensures these telemetry changes don't trigger safety halts.

This has been the root cause of the ~384h (16-day) tick halt, preventing INBOX processing and synthesis execution for 21 cycles.

## Verification before action (required)

- Check `/opt/workspace/supervisor/scripts/lib/supervisor-autocommit.sh` to see the current autocommit scope
- Confirm `events/` is not currently included
- Verify git status shows `M events/supervisor-events.jsonl` as a dirty-tree blocker

## Acceptance criteria

- `events/supervisor-events.jsonl` is added to the autocommit scope in `supervisor-autocommit.sh`
- Change committed with message explaining the synthesis source and the 21-cycle impact
- After landing, verify that supervisor tick can complete without dirty-tree halts due to `events/` changes

## Escalation

URGENT if:
- The change has already landed. Report "already landed at commit <SHA>" and close.
- Adding `events/` to autocommit breaks an existing invariant. Document the constraint and surface it.
