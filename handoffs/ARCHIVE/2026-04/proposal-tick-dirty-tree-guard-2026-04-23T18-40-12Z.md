---
from: synthesis-translator
to: general
date: 2026-04-23T18-40-12Z
priority: critical
task_id: synthesis-tick-dirty-tree-guard
source_synthesis: /opt/workspace/runtime/.meta/cross-cutting-2026-04-23T15-24-05Z.md
source_proposal: Proposal 1 — Fix `supervisor-tick.sh` dirty-tree guard (4th cycle, ROOT CAUSE)
---

# Fix `supervisor-tick.sh` dirty-tree guard (4th cycle, ROOT CAUSE)

## Problem

One untracked file (`supervisor/playbooks/positioning-test.md`) blocks the supervisor tick via the dirty-tree guard at `supervisor/scripts/lib/supervisor-tick.sh` line 134. The guard treats `??` (untracked) identically to `M`/`A`/`D` (modified/staged/deleted), despite untracked files posing zero merge-conflict risk.

**Cascade (92h and counting):**
- 31 INBOX items (29 identical tick-skip noise)
- ~46 tick cycles missed
- 0 telemetry events post-rotation (tick is the primary emitter)
- 0 automated INBOX processing
- 4 synthesis cycles documenting the same root cause
- 6 reflection cycles per project documenting the same root cause

This is now the 4th consecutive synthesis cycle reporting this root cause.

## Proposed Fix

**File**: `supervisor/scripts/lib/supervisor-tick.sh` line 134

**Current code:**
```bash
PRE_SUP_DIRTY=$(git -C "$SUP" status --porcelain 2>/dev/null || true)
```

**Proposed replacement:**
```bash
PRE_SUP_DIRTY=$(git -C "$SUP" status --porcelain 2>/dev/null | grep -v '^??' || true)
```

Untracked files cannot produce merge conflicts. Excluding them from the dirty-tree guard eliminates the failure class where an untracked artifact from an attended session blocks all automated execution indefinitely.

**Blast radius:** Supervisor tick only. Automatic once landed. All projects benefit through restored tick operation. Low risk — `??`-status files are definitionally not in conflict with any remote state.

## Rationale

The fix has been specified since 2026-04-21T15:26Z (3 synthesis cycles, 6 reflection cycles). The current cost of not applying this fix: 92h outage, 29 noise INBOX files, 4 synthesis cycles, ~46 missed tick cycles.

## Verification before action (required)

- Run `git log --oneline -20 supervisor/scripts/lib/supervisor-tick.sh` in `/opt/workspace/supervisor/`. Check if this exact change has already landed.
- Read the target file at the line specified. Verify the current state matches the "Current code" block above.
- If either verification shows the fix is already applied, write a completion report stating "already landed" rather than re-applying.

## Acceptance criteria

- Line 134 of `supervisor/scripts/lib/supervisor-tick.sh` is changed from the current code to the proposed replacement.
- Change is committed with a message explaining that this unblocks the tick (now stopped for 92h due to untracked file).
- Next supervisor-tick cycle runs successfully (validates that the fix works and doesn't introduce new blockers).
- Completion report confirms fix is applied and provides the commit SHA.

## Escalation

URGENT if:
- The change is already applied (skip with "already landed" note).
- Verification shows the file path or line number has drifted since the synthesis was written. Escalate with the new location.
- The fix causes a regression (tick fails for a different reason post-fix). Escalate with the new error.
