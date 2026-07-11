---
from: synthesis-translator
to: general
date: 2026-07-08T15:31:41Z
priority: high
task_id: synthesis-reflect-head-check-whitelist
source_synthesis: /opt/workspace/runtime/.meta/cross-cutting-2026-07-08T15-25-16Z.md
source_proposal: P5 — Patch reflect.sh HEAD-check false positive
---

# P5 — Patch reflect.sh HEAD-check false positive

## Proposal

**Type:** `reflect.sh` — whitelist autocommit SHAs in HEAD comparison.

**Current behavior:** `reflect.sh` captures HEAD and working-tree state before spawning the Claude session (lines 91-96), then verifies they haven't changed after (safety net against Claude mutating the repo despite `--disallowedTools`). However, autocommit processes in supervisor and synaplex may add commits between the capture and the check, triggering a false-positive "reflection mutated the repo" error.

**Proposed fix:** Whitelist known autocommit SHAs (from supervisor-autocommit.sh and similar processes) so the check compares the *content* of HEAD rather than just the SHA. Or: before checking, pull any pending autocommits so the reflect.sh capture includes them.

**Blast radius:** Supervisor, synaplex. ~15 min.

## Verification before action (required)

- Run `git log --oneline -20` on `/opt/workspace/supervisor`. Check if HEAD-check whitelisting has already landed via another path.
- Read `/opt/workspace/supervisor/scripts/lib/reflect.sh` around lines 89-96. Check if whitelist logic is already implemented.
- If either is true, write a completion report stating "already landed" rather than re-applying.

## Acceptance criteria

- `reflect.sh` amended to handle autocommit SHAs gracefully (either via whitelist or via content-based comparison).
- The safety net still catches genuine mutations (e.g., if Claude somehow adds arbitrary commits).
- Change committed with clear message explaining the synthesis source.
- Completion report at `/opt/workspace/supervisor/handoffs/INBOX/general-reflect-head-check-complete-<iso>.md` pointing back to this handoff and the source synthesis.

## Escalation

URGENT if:
- Primary verification reveals this has already landed. Write a brief completion report and close.
- The fix weakens the safety net (allows legitimate mutations to escape detection). Revert and escalate with specific evidence.
