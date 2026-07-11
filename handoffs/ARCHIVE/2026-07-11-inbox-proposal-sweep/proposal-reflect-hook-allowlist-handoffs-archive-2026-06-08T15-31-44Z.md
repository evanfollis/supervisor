---
from: synthesis-translator
to: general
date: 2026-06-08T15:31:44Z
priority: high
task_id: synthesis-reflect-hook-allowlist-handoffs-archive
source_synthesis: /opt/workspace/runtime/.meta/cross-cutting-2026-06-08T15-27-05Z.md
source_proposal: Proposal 3 — P-reflect-hook-allowlist — Filter session-end hook writes from dirty-tree check (CARRY-FORWARD, 5th cycle)
---

# P-reflect-hook-allowlist — Filter session-end hook writes from dirty-tree check

## Summary

Reflection sessions are permitted and expected to maintain CONTEXT.md and CURRENT_STATE.md via session-end hooks. Currently, other hook-generated files (e.g., handoffs in `handoffs/ARCHIVE/`) trigger false-positive URGENT warnings about unexpected working-tree mutations.

**Failure class:** Safety net with overly broad mutation detection produces false positives when legitimate automation-generated files land during reflection sessions.

## Proposed patch

Modify `/opt/workspace/supervisor/scripts/lib/reflect.sh` lines 172-173 to exclude archived handoffs in addition to CURRENT_STATE.md:

**Replace lines 172-173:**
```bash
BEFORE_DIRTY_FILTERED=$(echo "$BEFORE_DIRTY" | grep -vE '(CONTEXT|CURRENT_STATE)\.md|handoffs/ARCHIVE/' || true)
AFTER_DIRTY_FILTERED=$(echo "$AFTER_DIRTY" | grep -vE '(CONTEXT|CURRENT_STATE)\.md|handoffs/ARCHIVE/' || true)
```

This filters out any files in `handoffs/ARCHIVE/` (historical handoff records moved by session-end hooks) from the dirty-tree check, preventing false-positive URGENT warnings.

## Blast radius

Supervisor only. Eliminates false-positive URGENT handoffs from session-end hook writes.

## Verification before action (required)

- Run `git -C /opt/workspace/supervisor log --oneline -10` to verify the patch hasn't landed.
- Read `/opt/workspace/supervisor/scripts/lib/reflect.sh` lines 172-173 to confirm the `|handoffs/ARCHIVE/` filter is not yet present.
- If either shows the patch is already applied, write a completion report stating "already landed" rather than re-applying.

## Acceptance criteria

- Lines 172-173 in `reflect.sh` contain the grep filters including `|handoffs/ARCHIVE/`.
- Change committed with a message explaining the false-positive URGENT elimination.
- Adversarial review via `supervisor/scripts/lib/adversarial-review.sh` (touches safety-net logic).
- Completion report at `/opt/workspace/supervisor/handoffs/INBOX/general-reflect-allowlist-complete-<iso>.md` pointing back to this handoff.

## Escalation

URGENT if:
- The filter is too broad and suppresses legitimate working-tree mutation warnings (test with a project that had unintended file changes).
- Primary verification reveals this change was already applied (carry-forward became redundant).
