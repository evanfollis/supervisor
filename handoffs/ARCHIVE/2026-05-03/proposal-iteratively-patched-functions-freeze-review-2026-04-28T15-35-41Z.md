---
from: synthesis-translator
to: general
date: 2026-04-28T15:35:41Z
priority: high
task_id: synthesis-iteratively-patched-functions-freeze
source_synthesis: /opt/workspace/runtime/.meta/cross-cutting-2026-04-28T15-28-05Z.md
source_proposal: Proposal 1 — CLAUDE.md amendment — iteratively-patched functions must freeze for review after 3+ bug-fix commits
---

# CLAUDE.md amendment — Functions with 3+ bug-fix commits freeze for review

## Proposal body (from synthesis)

This addresses Pattern 2 (Design instability on iteratively-patched critical paths). The atlas and synaplex reflections both independently diagnosed the same failure class: a function that accumulates 3+ consecutive bug-fix commits without a clean invariant pass becomes design-unstable — each patch introduces the next failure mode. The existing `/review` rule triggers on "significant changes" but does not trigger on accumulated instability on the same function.

**Proposed text** (add to §Quality: Root-Cause Discipline, after "Understand the causal chain before proposing a fix"):

```
- **Functions with 3+ consecutive bug-fix commits freeze for redesign
  review.** If the same function or module has been the target of 3 or
  more consecutive bug-fix commits (not feature additions), freeze it
  for adversarial review before the next touch. The pattern of
  iterative patching — where each fix introduces the next failure mode
  — is a design instability signal. The review must produce a clean
  invariant statement for the function. If no clean invariant can be
  stated, the function needs a redesign, not another patch.
```

**Blast radius:** All projects. Policy-level — opt-in by reading CLAUDE.md. Does not block any automated workflow; adds a gate visible to reflections and reviews. Atlas's `_maybe_escalate_frozen_loop` (5 bugs / 5 commits) and synaplex's cap enforcement path would both trigger this gate immediately.

---

## Verification before action (required)

- [x] Checked `/opt/workspace/CLAUDE.md` — text does not exist
- [x] Checked git history — no matching amendment landed by another path
- [x] This is new, non-duplicated proposal for this synthesis cycle

## Acceptance criteria

- [ ] The proposed text is added to `/opt/workspace/CLAUDE.md`, section §Quality: Root-Cause Discipline, immediately after the "Understand the causal chain before proposing a fix" bullet
- [ ] Committed with clear message: "Charter: require redesign review for functions with 3+ consecutive bug-fix commits" (or equivalent)
- [ ] No adversarial review required (policy amendment, not code change)
- [ ] Completion report written to `/opt/workspace/runtime/.handoff/general-supervisor-synthesis-iteratively-patched-functions-freeze-complete-2026-04-28T<time>Z.md` pointing back to this handoff

## Escalation

- URGENT if the synthesis is already stale (run `git log -1 --format=%ai /opt/workspace/CLAUDE.md` to check)
- Mark as "already landed" if the text is verified in-file before starting

## Notes

This is a straightforward charter amendment. No code changes, no deployment, no external coordination. The text is explicit and ready to land. The two projects that would immediately trigger this gate (atlas and synaplex) are both identified in the synthesis.
