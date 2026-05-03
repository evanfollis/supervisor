---
from: synthesis-translator
to: general
date: 2026-05-01T15:32:17Z
priority: high
task_id: synthesis-iterate-patch-freeze-gate
source_synthesis: /opt/workspace/runtime/.meta/cross-cutting-2026-05-01T15-28-00Z.md
source_proposal: "Proposal 1 [CRITICAL, REPEAT — 10th cycle]: CLAUDE.md amendment — iterate-patch-freeze gate"
---

# CLAUDE.md amendment — iterate-patch-freeze gate

## Summary

Add a new bullet to §Quality: Root-Cause Discipline in `/opt/workspace/CLAUDE.md` establishing a gate that freezes iteratively-patched functions behind adversarial review. Any function that has been patched 3+ times for distinct bug classes must pass `/review` or `adversarial-review.sh` before the next commit touching it.

## Proposed text

Add to §Quality: Root-Cause Discipline, after the "Understand the causal chain" bullet:

```
- **Freeze iteratively-patched functions behind adversarial review.**
  Any function that has been patched 3+ times for distinct bug classes
  must pass adversarial review (`/review` or `adversarial-review.sh`)
  before the next commit that touches it. The threshold exists because
  functions with 3+ distinct fixes have a demonstrated >50% rate of
  introducing a new failure in the same commit that "fixes" the prior
  one. The atlas `_maybe_escalate_frozen_loop` function (7 bugs across
  6 commits, 5 consecutive /review skips) is the motivating case.
```

## Why this proposal

This gate has been proposed for 10 cycles and empirically validated: the atlas function that motivated it accumulated 7 bugs across 6 commits with 5 consecutive review skips. The prior window confirmed the root cause to specific lines. Any review — even a degraded one — would have caught bug #7. This is the single highest-leverage rule not yet in CLAUDE.md.

**Status**: 5 existing INBOX copies from prior synthesis cycles.

## Verification before action (required)

- Run `git log --oneline -20` on `/opt/workspace/`. Check if this text has already been added to CLAUDE.md via another path.
- Read `/opt/workspace/CLAUDE.md` and search for "iterate" or "3+ times" or "patched functions". If found, this proposal has already landed.

## Acceptance criteria

- The proposed bullet is added to `/opt/workspace/CLAUDE.md` at the specified location (§Quality: Root-Cause Discipline, after "Understand the causal chain").
- Single commit with clear message: "Add iterate-patch-freeze gate to CLAUDE.md (Proposal 1, 10th cycle)"
- Commit must explain the synthesis source and empirical validation in the message body.

## Escalation

URGENT if:
- The text is already in CLAUDE.md from a prior commit. Write a completion report saying "already landed at commit <SHA>" and close.
- A more recent decision in `supervisor/decisions/` conflicts with this proposal (e.g., reject adversarial review as a gate). Surface the conflict.
