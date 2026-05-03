---
from: synthesis-translator
to: general
date: 2026-04-28T15:34:37Z
priority: high
task_id: synthesis-iterate-patch-freeze-rule
source_synthesis: /opt/workspace/runtime/.meta/cross-cutting-2026-04-28T15-28-05Z.md
source_proposal: Proposal 1 [HIGH] — CLAUDE.md amendment on iteratively-patched function freeze
---

# CLAUDE.md amendment — iteratively-patched functions must freeze for review after 3+ bug-fix commits

## Context

Two critical-path functions (atlas `_maybe_escalate_frozen_loop` and synaplex cap enforcement) have each accumulated 3+ consecutive bug-fix commits without a clean invariant pass. Each patch introduces the next failure mode — a design instability signal. The atlas function has 5 distinct bug classes in 5 commits over 3 days.

**Synthesis diagnosis (Pattern 2):** This is a code design problem, separate from the EROFS sandbox/execution bottleneck. Both functions need clean redesign, not another patch.

**Solution:** Add a governance gate to CLAUDE.md that requires adversarial review (freeze for redesign) when a function accumulates 3+ consecutive bug-fix commits.

## Proposed text

Add the following bullet to `/opt/workspace/CLAUDE.md` in the section `### Quality: Root-Cause Discipline`, after the existing bullet "Understand the causal chain before proposing a fix":

```
- **Functions with 3+ consecutive bug-fix commits freeze for redesign review.** If the same function or module has been the target of 3 or more consecutive bug-fix commits (not feature additions), freeze it for adversarial review before the next touch. The pattern of iterative patching — where each fix introduces the next failure mode — is a design instability signal. The review must produce a clean invariant statement for the function. If no clean invariant can be stated, the function needs a redesign, not another patch.
```

**File path:** `/opt/workspace/CLAUDE.md`
**Target section:** `### Quality: Root-Cause Discipline`
**Insertion point:** After the bullet starting with "Understand the causal chain before proposing a fix"

## Verification before action

- [ ] `grep -n "Understand the causal chain" /opt/workspace/CLAUDE.md` confirms the insertion point exists
- [ ] `grep -c "3+ consecutive bug-fix commits" /opt/workspace/CLAUDE.md` returns 0 (proposed text not already present)
- [ ] `git log --oneline -30` on supervisor repo shows no recent landing of this text

All three checks pass — this proposal is not yet landed.

## Acceptance criteria

- The proposed bullet is inserted into `/opt/workspace/CLAUDE.md` after the "Understand the causal chain" bullet
- Commit message explains the synthesis source and root causes (atlas and synaplex pattern instability)
- `git diff HEAD~1 CLAUDE.md` shows only the proposed addition, no other edits
- Write completion report to `/opt/workspace/runtime/.handoff/general-supervisor-synthesis-iterate-patch-freeze-complete-<iso>.md` pointing back to this handoff

## Notes

- No adversarial review needed for this proposal (it's a governance text addition, not code)
- Blast radius: all projects; policy-level — opt-in by reading CLAUDE.md
- This gate will immediately flag atlas `_maybe_escalate_frozen_loop` (5 bugs/5 commits) and synaplex cap enforcement path for redesign review
- Synthesis source explicitly requested this amendment; no further scope expansion needed
