---
from: synthesis-translator
to: general
date: 2026-06-10T15:36:31Z
priority: critical
task_id: synthesis-events-autocommit-scope
source_synthesis: /opt/workspace/runtime/.meta/cross-cutting-2026-06-10T15-26-21Z.md
source_proposal: "Proposal 2 — P2-promoted UNCHANGED — Add `events/` to autocommit Tier-A scope (sole tick blocker)"
---

# Add `events/` to autocommit Tier-A scope (sole tick blocker)

## Proposal

**Identical to C89 Proposed change #1. This is the sole remaining tick blocker.**

Supervisor autocommit currently excludes `events/supervisor-events.jsonl`. The tick appends to this file, making the working tree dirty. The autocommit job stages only `friction/ handoffs/ system/ ideas/ decisions/` — the next tick sees a dirty tree and skips. Skip counter is now at **10 consecutive**. This has been documented since C60 (31+ cycles, ~16 days).

### Required change

Edit `supervisor/scripts/lib/supervisor-autocommit.sh`:

**Lines 55-56** (check for dirty Tier-A paths):
```bash
TIER_A_DIRTY=$(git -C "$SUP" status --porcelain \
  -- friction/ handoffs/ system/ ideas/ decisions/ events/ 2>/dev/null || true)
```

**Lines 61-62** (stage Tier-A paths):
```bash
git -C "$SUP" add \
  friction/ handoffs/ system/ ideas/ decisions/ events/ \
  2>/dev/null || true
```

### Impact

- Supervisor autocommit will now include `events/` in Tier-A scope
- The tick's event-write will no longer leave the tree dirty
- The 10-cycle skip streak breaks
- This unblocks the governance cascade

**Blast radius**: Supervisor autocommit only (automatic).

**History**: This is the 32nd consecutive synthesis cycle recommending this change (since C60).

## Verification before action (required)

- Run `git log --oneline -5 -- supervisor/scripts/lib/supervisor-autocommit.sh` and confirm `events/` has not been added to lines 55-56 or 61-62.
- Read the current state of those lines in the file.
- Confirm the skip counter is still at or near 10 consecutive (check `supervisor-reflection-` files in `.meta/`).

## Acceptance criteria

- Both line ranges (55-56 and 61-62) now include `events/` in the path list
- Change committed with a message explaining this unblocks the tick
- Next supervisor tick runs successfully (does not skip due to dirty events/)
- Completion report at `runtime/.handoff/general-supervisor-synthesis-events-autocommit-complete-<iso>.md` pointing back to this handoff and C60+ prior context

## Escalation

URGENT if:
- Git log shows this landed already by another path. Write completion report: "already landed at commit <SHA>".
- The skip streak has grown beyond 10 consecutive. Inspect the tick logs for the root cause — either a new blocker has appeared, or the prior fix attempt was incomplete.
