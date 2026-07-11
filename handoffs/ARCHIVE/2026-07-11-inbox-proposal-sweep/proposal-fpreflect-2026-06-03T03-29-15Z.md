---
from: synthesis-translator
to: general
date: 2026-06-03T03:29:15Z
priority: medium
task_id: synthesis-fpreflect
source_synthesis: /opt/workspace/runtime/.meta/cross-cutting-2026-06-03T03-23-01Z.md
source_proposal: P-fpreflect (Real: reflect.sh false-positive on INBOX archiving)
---

# Scope reflect.sh HEAD check to exclude archive operations

## Problem

The reflection session's normal INBOX archiving operation (`handoffs/ARCHIVE/` writes) is triggering the dirty-tree safety check in `reflect.sh`, generating a false-positive URGENT handoff (`URGENT-supervisor-reflection-dirty-tree.md`). The safety net cannot distinguish legal archive operations (part of supervisor reentry hygiene) from unauthorized mutations.

## Proposed fix

Narrow the HEAD check in `/opt/workspace/supervisor/scripts/lib/reflect.sh` (lines 172–173) to exclude `handoffs/ARCHIVE/` from the dirty-tree detection, alongside the already-excluded `CONTEXT.md` and `CURRENT_STATE.md`.

**Current code (lines 172–173):**
```bash
  BEFORE_DIRTY_FILTERED=$(echo "$BEFORE_DIRTY" | grep -vE '(CONTEXT|CURRENT_STATE)\.md' || true)
  AFTER_DIRTY_FILTERED=$(echo "$AFTER_DIRTY" | grep -vE '(CONTEXT|CURRENT_STATE)\.md' || true)
```

**Target code:**
```bash
  BEFORE_DIRTY_FILTERED=$(echo "$BEFORE_DIRTY" | grep -vE '(CONTEXT|CURRENT_STATE)\.md|handoffs/ARCHIVE' || true)
  AFTER_DIRTY_FILTERED=$(echo "$AFTER_DIRTY" | grep -vE '(CONTEXT|CURRENT_STATE)\.md|handoffs/ARCHIVE' || true)
```

The additional `|handoffs/ARCHIVE` alternation in the grep pattern will exclude archive paths from the mutation detection, preventing false positives while still catching actual unauthorized changes.

## Verification before action (required)

- Run `git log --oneline -20` on `/opt/workspace/supervisor`. Check if this proposal has already landed via another path.
- Read `/opt/workspace/supervisor/scripts/lib/reflect.sh` lines 172–173. Check if the grep pattern already includes `handoffs/ARCHIVE`.
- If either is true, write a completion report stating "already landed at commit <SHA> / verified in-file" rather than re-applying.

## Acceptance criteria

- The grep pattern on lines 172–173 includes `|handoffs/ARCHIVE` to exclude archive writes from dirty-tree detection.
- Reflection sessions no longer generate `URGENT-<project>-reflection-dirty-tree.md` for normal INBOX archiving operations.
- Change committed with imperative message explaining the synthesis source and FR-NEXT-F identifier.
- Completion report at `/opt/workspace/runtime/.handoff/general-supervisor-synthesis-fpreflect-complete-<iso>.md` pointing back to this handoff and the source synthesis.

## Escalation

URGENT if:
- Primary verification reveals the proposal is based on stale state (already landed by another path between synthesis run and this handoff). Write a brief completion report saying "obsolete — already landed" and close.
- The proposal conflicts with a more recent decision in `supervisor/decisions/`. Do not force-apply; escalate with the conflict named.
