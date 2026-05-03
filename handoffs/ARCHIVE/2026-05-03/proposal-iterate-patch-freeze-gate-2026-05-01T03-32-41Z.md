---
from: synthesis-translator
to: general
date: 2026-05-01T03:32:41Z
priority: high
task_id: synthesis-iterate-patch-freeze-gate
source_synthesis: /opt/workspace/runtime/.meta/cross-cutting-2026-05-01T03-27-05Z.md
source_proposal: Proposal 1 — Iterate-patch-freeze gate (CRITICAL, REPEAT — now empirically validated)
---

# Iterate-patch-freeze gate — CLAUDE.md amendment

**Pattern:** Functions patched 3+ times for distinct bugs have >50% rate of introducing new failures. Atlas `_maybe_escalate_frozen_loop` is the case study: 7 bugs across 6 commits, 5 consecutive /review skips, commit `9708867` (Apr 30 14:29Z, claimed to fix bug #6) introduced bug #7. The proposal was speculative 5 synthesis cycles ago; it is now empirically validated with 11 consecutive cycle failures post-deploy.

**Proposed text** (add to §Quality: Root-Cause Discipline in `/opt/workspace/CLAUDE.md`, after the "Understand the causal chain" bullet):

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

**Blast radius:** All projects. Policy-level, automatic by reading CLAUDE.md. Does not block normal development — only triggers on functions already known to be fragile.

**Why now:** 5 INBOX copies across 4 synthesis cycles. The predicted consequence materialized: `9708867` introduced bug #7 while claiming to fix bug #6. Single highest-leverage workspace rule not yet in CLAUDE.md.

## Verification before action (required)

- Run `git log --oneline -10 /opt/workspace/CLAUDE.md` to confirm no similar amendment landed.
- Run `grep -n "Freeze iteratively-patched" /opt/workspace/CLAUDE.md` — should return empty.
- If either check shows the amendment is already present, skip and report "already landed at commit <SHA>".

## Acceptance criteria

- Text added to CLAUDE.md at the specified location in §Quality: Root-Cause Discipline.
- Commit message: "Add iterate-patch-freeze gate to CLAUDE.md — functions patched 3+ times require adversarial review before next touch" (imperative, explains why not what).
- Commit includes cite to synthesis: `source_synthesis: /opt/workspace/runtime/.meta/cross-cutting-2026-05-01T03-27-05Z.md`.

## No adversarial review needed

This is a charter-level policy amendment copying text from the synthesis proposal verbatim. Adversarial review of the policy itself (scope, threshold, wording) is not needed — the synthesis already did that work across 5 cycles. Review would be circular.

## Completion report

After commit, write `/opt/workspace/runtime/.handoff/general-supervisor-synthesis-iterate-patch-freeze-complete-<iso>.md` with:
- Commit SHA
- Confirmation that grep verifies text is present
- Link back to this handoff
