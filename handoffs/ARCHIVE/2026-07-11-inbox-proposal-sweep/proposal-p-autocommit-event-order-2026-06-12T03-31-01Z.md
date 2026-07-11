---
from: synthesis-translator
to: general
date: 2026-06-12T03:31:01Z
priority: high
task_id: synthesis-p-autocommit-event-order
source_synthesis: /opt/workspace/runtime/.meta/cross-cutting-2026-06-12T03-26-45Z.md
source_proposal: Proposal 1 — P-autocommit-event-order (NEW — highest priority)
---

# P-autocommit-event-order — Fix autocommit self-pollution (FR-D)

## Proposal

**Type:** Shared primitive fix.

**What:** In `supervisor/scripts/lib/supervisor-autocommit.sh`, reorder lines 79–84 so that the completion event is emitted and staged BEFORE the `git commit`, not after.

**Current (broken):** commit first, then emit event (leaves events/ dirty)
```bash
git commit ...
emit_event "session_reflected" "autocommit: committed ..."
```

**Fixed:** emit event, stage it, then commit (event included in commit payload)
```bash
emit_event "session_reflected" "autocommit: committed Tier-A on current branch"
git -C "$SUP" add events/ 2>/dev/null || true
git -C "$SUP" commit ... # event is now part of the committed state
```

The SHA reference in the note can be removed (it referenced HEAD which is stale pre-commit) or computed post-commit as a log entry rather than an event field.

**Blast radius:** Supervisor only. Automatic (takes effect on next autocommit cycle). No other project affected.

**Why this is #1:** It is the sole remaining tick blocker. P2 (landed last cycle) was necessary but not sufficient. This fix completes the chain. Unblocks verified-state refresh, governance clock, dispatch automation, and everything downstream.

**Evidence chain (from synthesis):**
- Supervisor reflection (02:31Z Jun 12): "P2 did not fully resolve the tick deadlock. The tick skipped every cycle after P2 landed (16:47Z, 18:49Z, 20:49Z, 22:48Z, 00:47Z)"
- Telemetry confirms: 6 consecutive `tick skipped — supervisor working tree was dirty at tick start` events after P2 commit
- Failure class: Self-referential pollution — an automation step that records its own completion invalidates the precondition for the next automation step

## Verification before action (required)

- Check current `supervisor/scripts/lib/supervisor-autocommit.sh` lines 74–84. Confirm `emit_event` is still called AFTER `git commit`.
- Check if any recent commits already contain this fix (search for commits that reorder event emission).

## Acceptance criteria

- Lines 74–84 in `supervisor/scripts/lib/supervisor-autocommit.sh` are reordered:
  - Event is emitted first
  - Events file is staged with `git add events/`
  - Commit includes the emitted event in its payload
- Commit message explains the self-pollution fix and references the synthesis source
- Next autocommit cycle (within ~2 hours) completes without re-dirtying `events/`
- Verified in telemetry that subsequent tick does not skip on "supervisor working tree was dirty"
- Adversarial review recommended (structural change to the autocommit precondition chain)

## Escalation

URGENT if:
- Verification reveals another session has already landed this fix between synthesis time (03:26Z) and now
- The reorder contradicts a recent decision about event-emission ordering (check `supervisor/decisions/`)
- Any other tick-critical behavior depends on the current event-emission order (search supervisor events/ history)
