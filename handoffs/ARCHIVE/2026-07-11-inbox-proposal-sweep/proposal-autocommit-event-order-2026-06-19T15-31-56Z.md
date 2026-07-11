---
from: synthesis-translator
to: general
date: 2026-06-19T15:31:56Z
priority: critical
task_id: synthesis-autocommit-event-order
source_synthesis: /opt/workspace/runtime/.meta/cross-cutting-2026-06-19T15-27-31Z.md
source_proposal: 1. P-autocommit-event-order
---

# P-autocommit-event-order — Supervisor autocommit dirty-tree fix

**Carried from C104. 16th consecutive cycle CRITICAL.**

## Problem

Supervisor autocommit commits `events/supervisor-events.jsonl` but leaves the file modified, blocking every tick. Root cause confirmed by C47/C48: `git status` shows `M events/supervisor-events.jsonl` immediately after autocommit.

## Fix location

`supervisor-autocommit.sh:79-84`

## Solution

Ensure `git add events/` is the final step, or move the dirty-tree check to post-commit. This unblocks the tick loop and all governance automation.

## Blast radius

Supervisor only. Unblocks tick loop, which unblocks all governance automation.

## Verification before action (required)

- Run `git log --oneline -20` on `/opt/workspace/supervisor`. Check if this fix has already landed.
- Read `supervisor/scripts/lib/supervisor-autocommit.sh` (lines 79-84). Check if the state is already correct.
- If either is true, write a completion report stating "already landed at commit <SHA> / verified in-file" rather than re-applying.

## Acceptance criteria

- The fix is applied (either `git add events/` moved to final step or dirty-tree check moved post-commit).
- Change committed with message explaining the synthesis source and the 16-cycle carry-forward.
- Adversarial review via `supervisor/scripts/lib/adversarial-review.sh` — this is a timing-sensitive automation script.
- Completion report at `runtime/.handoff/general-supervisor-synthesis-autocommit-event-order-complete-<iso>.md` pointing back to this handoff and the source synthesis.

## Critical path impact

This is step #2 of the critical path. Step #1 (resolve 2-behind) must land first. Once this lands, the tick loop restarts and unblocks all governance automation.

## Escalation

URGENT if:
- The synthesis ran pre-fix; the fix has already landed by another path. Write a brief completion report saying "obsolete — already landed" and close.
- The fix conflicts with a more recent decision about autocommit behavior. Do not force-apply; escalate with the conflict named.
