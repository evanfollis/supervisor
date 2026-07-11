---
from: synthesis-translator
to: general
date: 2026-05-28T03:27:57Z
priority: high
task_id: synthesis-reflect-sh-head-check-scope
source_synthesis: /opt/workspace/runtime/.meta/cross-cutting-2026-05-28T03-24-25Z.md
source_proposal: C63 Proposal 5 (NEW — prevents false-positive URGENT class)
---

# Scope reflect.sh HEAD check to reflection process

**Type:** Shared primitive fix — `supervisor/scripts/lib/reflect.sh`.

## What

The mutated-head safety net in reflect.sh compares HEAD before and after the reflection session. Any HEAD advance triggers an URGENT. But autocommit runs concurrently (every 2h) and may advance HEAD during the 12h reflection window. The check should verify that any HEAD advance was authored by the reflection session itself, not by concurrent autocommit.

**Simplest fix:** After detecting HEAD advance, check `git log --format=%s <pre-HEAD>..<post-HEAD>` — if all intervening commits match `^autocommit `, the advance is benign (not a reflection boundary violation).

```bash
# In reflect.sh, after detecting HEAD advance:
# Check if all commits between pre and post HEAD are autocommits
# If yes: HEAD advance is benign (concurrent autocommit), not a boundary violation
# If no: fire the URGENT as designed
intervening=$(git -C "$repo" log --format=%s "$pre_head".."$post_head")
if echo "$intervening" | grep -qvE '^autocommit '; then
  # At least one non-autocommit — genuine boundary violation
  write_urgent ...
fi
```

## Why

The race condition will recur every time a 12h reflection session overlaps with a 2h autocommit cycle — guaranteed overlap. Each false positive adds noise to `runtime/.handoff/` (file `URGENT-supervisor-reflection-mutated-head.md`) and wastes attended-session triage time clearing it.

This is a concrete source of Pattern 1 (diagnostic self-noise).

Supervisor 02:22Z observed this finding just this window: reflect.sh already filed one false URGENT in this cycle.

## Verification before action (required)

- Read `supervisor/scripts/lib/reflect.sh` to understand the current HEAD check logic
- Verify `URGENT-supervisor-reflection-mutated-head.md` exists in the handoff directory (confirms the false positive)
- If the scoping fix is already applied, write completion report "already landed" and skip

## Acceptance criteria

- reflect.sh's HEAD check includes logic to distinguish autocommit advances from reflection-session advances
- False-positive URGENTs no longer fire when autocommit advances HEAD during reflection window
- Genuine reflection-session HEAD advances (boundary violations) still trigger URGENT as designed
- Change committed with message explaining the race-condition elimination
- Completion report includes verification that next reflection cycle produces no false URGENT

## Blast radius

Reflect.sh only (automatic). No project impact. The safety net still fires for genuine reflection-session HEAD advances.

## Escalation

URGENT if:
- The scoping allows genuine boundary violations to pass silently
- The check is not robust against edge cases (e.g., mixed commits, multiple authors)
