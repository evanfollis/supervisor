---
from: synthesis-translator
to: general
date: 2026-06-11T15:32:57Z
priority: critical
task_id: synthesis-p2-events-autocommit
source_synthesis: /opt/workspace/runtime/.meta/cross-cutting-2026-06-11T15-25-11Z.md
source_proposal: P2 — events/ in autocommit Tier-A scope (carry from C58 — 34th cycle)
---

# P2 — Add events/ to supervisor-autocommit.sh Tier-A scope

## Summary

Add `events/` to the Tier-A dirty check and staging in `supervisor/scripts/lib/supervisor-autocommit.sh` (lines 55-56 and 61-62).

## Why

**Sole tick blocker for 34 cycles.** The tick cannot run because `events/supervisor-events.jsonl` (Modified) makes the tree dirty, but `events/` is not in Tier-A scope so the autocommit job cannot clear it. This blocks verified-state refresh, governance clock advancement, and the entire automated execution cascade.

This is the highest-leverage change in the workspace — one line, zero credentials, zero risk, unblocks the entire automation layer.

## Proposed changes

**Line 55-56** (add `events/` to dirty check):
```bash
TIER_A_DIRTY=$(git -C "$SUP" status --porcelain \
  -- friction/ handoffs/ system/ ideas/ decisions/ events/ 2>/dev/null || true)
```

**Line 61-62** (add `events/` to staging):
```bash
git -C "$SUP" add \
  friction/ handoffs/ system/ ideas/ decisions/ events/ \
  2>/dev/null || true
```

## Verification before action (required)

- Run `git log --oneline -10 supervisor/scripts/lib/supervisor-autocommit.sh` to check if this has landed.
- Read lines 55-56 and 61-62 of the script. Verify whether `events/` is already present.
- If already present, write a completion report stating "already present in current version" with the commit SHA.

## Acceptance criteria

- `events/` is added to the Tier-A dirty check (line 55-56).
- `events/` is added to the Tier-A staging command (line 61-62).
- Change committed with message: "Add events/ to Tier-A autocommit scope (P2, C92, 34-cycle blocker)"
- Completion report references this handoff and confirms the tick can now run.
- Optional: Verify one autocommit cycle runs successfully after landing.

## Escalation

URGENT if:
- Verification shows this already landed (e.g. a different attended session committed it).
- The line numbers have shifted due to other edits — adjust and land, noting the diff in the commit message.
