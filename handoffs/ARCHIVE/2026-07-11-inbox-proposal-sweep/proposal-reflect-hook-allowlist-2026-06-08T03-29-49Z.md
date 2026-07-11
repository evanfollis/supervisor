---
from: synthesis-translator
to: general
date: 2026-06-08T03:29:49Z
priority: high
task_id: synthesis-reflect-hook-allowlist
source_synthesis: /opt/workspace/runtime/.meta/cross-cutting-2026-06-08T03-25-09Z.md
source_proposal: Proposal 2 — P-reflect-hook-allowlist
---

# Filter session-end hook writes from dirty-tree check

## Problem

The reflect.sh dirty-tree validation (lines 172–173) filters out `CONTEXT.md` and `CURRENT_STATE.md` writes, but does not exclude writes from the session-end hook (which writes to `handoffs/ARCHIVE/`). This causes false-positive URGENT escalations when the session-end hook runs and writes to the archive directory during reflection.

This is the 4th consecutive cycle of this proposal.

## Solution

Update `supervisor/scripts/lib/reflect.sh` to exclude hook-generated files from the dirty-tree check.

**Replace lines 172–173:**
```bash
BEFORE_DIRTY_FILTERED=$(echo "$BEFORE_DIRTY" | grep -vE '(CONTEXT|CURRENT_STATE)\.md' || true)
AFTER_DIRTY_FILTERED=$(echo "$AFTER_DIRTY" | grep -vE '(CONTEXT|CURRENT_STATE)\.md' || true)
```

**With:**
```bash
BEFORE_DIRTY_FILTERED=$(echo "$BEFORE_DIRTY" | grep -vE '(CONTEXT|CURRENT_STATE)\.md|handoffs/ARCHIVE/' || true)
AFTER_DIRTY_FILTERED=$(echo "$AFTER_DIRTY" | grep -vE '(CONTEXT|CURRENT_STATE)\.md|handoffs/ARCHIVE/' || true)
```

## Verification before action (required)

- Run `git log --oneline -- supervisor/scripts/lib/reflect.sh | head -5` on `/opt/workspace/supervisor`. Verify the most recent commit to this file.
- Read `supervisor/scripts/lib/reflect.sh` lines 172–173. Verify that they match the current state described in the synthesis (filtering only `CONTEXT|CURRENT_STATE` without the `handoffs/ARCHIVE/` pattern).
- If both checks pass, proceed with the edit.

## Acceptance criteria

- Lines 172–173 of `supervisor/scripts/lib/reflect.sh` include the `handoffs/ARCHIVE/` exclusion pattern
- Change committed with message: "reflect.sh: exclude session-end hook archive writes from dirty-tree check"
- Include `Co-Authored-By: synthesis-translator <noreply@synthesis>` in the commit trailer
- Completion report at `/opt/workspace/supervisor/handoffs/INBOX/general-proposal-reflect-hook-allowlist-complete-<iso>.md`

## Blast radius

Supervisor only. This change eliminates false-positive URGENT generation from session-end hook writes. Independent of Proposal 1 and Proposal 3 (P1).

## Escalation

URGENT if:
- Primary verification reveals this change is already landed. Write a completion report saying "already landed at commit <SHA>" and close.
- The proposal conflicts with a more recent decision recorded in `supervisor/decisions/`. Surface the conflict and the decision reference.
