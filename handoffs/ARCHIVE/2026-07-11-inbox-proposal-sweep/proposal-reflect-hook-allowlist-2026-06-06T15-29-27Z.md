---
from: synthesis-translator
to: general
date: 2026-06-06T15:29:27Z
priority: high
task_id: synthesis-reflect-hook-allowlist
source_synthesis: /opt/workspace/runtime/.meta/cross-cutting-2026-06-06T15-24-15Z.md
source_proposal: "Proposal 2: P-reflect-hook-allowlist — Allowlist session-end hook writes in reflect.sh safety net (NEW)"
---

# P-reflect-hook-allowlist — Filter known-safe hook writes from dirty-tree check

## Summary

The `reflect.sh` safety net compares the working tree before and after the reflection session to catch boundary violations. However, every reflection session triggers a **session-end auto-summary hook** (fired by `claude -p` after the session completes) that writes summary files into `supervisor/handoffs/ARCHIVE/<date>/`. These writes are benign — they're automation artifacts, not model-boundary violations — but the safety net treats them as mutations and generates false-positive URGENT escalations.

**Evidence:** Cycle 22 identified that the C21 reflection session's `handoffs/ARCHIVE/2026-06-06/` directory appeared in `git status --porcelain` AFTER the session exited, triggering a false-positive dirty-tree URGENT. Investigation confirmed the writes came from the session-end hook, not the Claude model.

**Impact:** Each false-positive URGENT adds noise to the backlog (currently 9 URGENT files in runtime/.handoff/). Eliminates genuine signal.

## Proposal details

Filter `handoffs/ARCHIVE/` from the dirty-tree comparison, the same way `CONTEXT.md` and `CURRENT_STATE.md` are already filtered.

## Change

**File:** `supervisor/scripts/lib/reflect.sh`

**Lines ~172-173 (in the safety net's dirty-tree check):** Extend the grep filter to exclude `handoffs/ARCHIVE/`:

```bash
# Before (lines 172-173):
BEFORE_DIRTY_FILTERED=$(echo "$BEFORE_DIRTY" | grep -vE '(CONTEXT|CURRENT_STATE)\.md' || true)
AFTER_DIRTY_FILTERED=$(echo "$AFTER_DIRTY" | grep -vE '(CONTEXT|CURRENT_STATE)\.md' || true)

# After:
BEFORE_DIRTY_FILTERED=$(echo "$BEFORE_DIRTY" | grep -vE '(CONTEXT|CURRENT_STATE)\.md|handoffs/ARCHIVE/' || true)
AFTER_DIRTY_FILTERED=$(echo "$AFTER_DIRTY" | grep -vE '(CONTEXT|CURRENT_STATE)\.md|handoffs/ARCHIVE/' || true)
```

## Verification before action (required)

Run these before proceeding:

```bash
cd /opt/workspace
git log --oneline -5 supervisor/scripts/lib/reflect.sh
```

Check: Is there a recent commit that already adds `handoffs/ARCHIVE/` to the grep filter? If yes, this proposal is already landed.

```bash
sed -n '172,173p' supervisor/scripts/lib/reflect.sh
```

Check: What filters are currently active in the BEFORE_DIRTY/AFTER_DIRTY lines?

## Acceptance criteria

- `supervisor/scripts/lib/reflect.sh` lines 172-173 include `handoffs/ARCHIVE/` in the grep `-v` exclusion pattern
- Change committed with message: "Filter session-end hook writes from reflect.sh dirty-tree check — reduces false-positive URGENTs"
- No adversarial review needed (isolated grep filter, low risk)
- Completion report: `/opt/workspace/runtime/.handoff/general-supervisor-synthesis-reflect-hook-allowlist-complete-<iso>.md`

## Escalation

URGENT if:
- Commit history shows this change already landed within the past 3 cycles
- The grep filter syntax differs from the example (verify the exact pattern against the surrounding code)

## Notes

This is one of three related reflect.sh improvements proposed in synthesis cycle 82 (see also: proposal-write-block and proposal-self-sustaining-fix). All three target the same file and could be landed together in a single attended session (~5 min total).

**Tradeoff note (from synthesis):** If the model itself writes to `handoffs/ARCHIVE/`, this filter would mask that. Acceptable because: (a) the session-end hook is the dominant writer there, (b) `handoffs/ARCHIVE/` is a low-risk location (it's an archive, not live state), and (c) the prompt contract + `--disallowedTools` remain the primary boundary.
