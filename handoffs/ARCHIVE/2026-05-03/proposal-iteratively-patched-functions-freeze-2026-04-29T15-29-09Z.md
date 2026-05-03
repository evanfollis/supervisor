---
from: synthesis-translator
to: general
date: 2026-04-29T15:29:09Z
priority: medium
task_id: synthesis-iteratively-patched-functions-freeze
source_synthesis: /opt/workspace/runtime/.meta/cross-cutting-2026-04-29T15-24-48Z.md
source_proposal: Proposal 3 [MEDIUM, repeat] — CLAUDE.md amendment — iteratively-patched functions freeze for review
---

# CLAUDE.md amendment — iteratively-patched functions freeze for review

**Type:** Policy-level amendment to `/opt/workspace/CLAUDE.md`.

This is a repeat proposal. The synthesis notes: "Same proposal as prior 2 syntheses. Not landed. INBOX now has 3 items for this (2 duplicates + 1 new from this cycle's translator). The exact text is unchanged from the prior synthesis."

**Blast radius:** All projects. Policy-level, opt-in. Does not block automated workflows.

## Proposal context

This proposal has been waiting since Apr 28 15:34Z (5+ days, across 3 synthesis cycles). Standing recommendations show:

| Entry | Date | Status |
|-------|------|--------|
| Iterate-patch-freeze (1st copy) | Apr 28 15:34Z | 2 cycles unlanded |
| Iterate-patch-freeze (dup of #1) | Apr 28 15:35Z | 2 cycles unlanded |
| Iterate-patch-freeze (dup) | Apr 29 03:28Z | 1 cycle unlanded |

## Verification before action (required)

- Read `/opt/workspace/supervisor/handoffs/INBOX/` and locate the prior proposal files for this amendment (filenames containing `freeze`, `iteratively-patched`, or `iterate-patch-freeze`). Extract the detailed proposal body from the earliest dated file.
- Run `git log --oneline -20` on supervisor repo. Check if this amendment has already been committed.
- Read `/opt/workspace/CLAUDE.md` and search for `freeze` or related keywords mentioned in the detailed proposal. Check if the amendment is already present.
- If the amendment is already in the file or committed, write a completion report stating "already landed at commit <SHA> / verified in-file" rather than re-applying.

## Acceptance criteria

- The CLAUDE.md amendment is applied (or verified already applied).
- Change committed with message: `Add iteratively-patched functions freeze rule to CLAUDE.md` or equivalent.
- Completion report at `runtime/.handoff/general-supervisor-synthesis-iteratively-patched-functions-freeze-complete-<iso>.md` pointing back to this handoff and the source INBOX item used.

## Deduplication note

The synthesis notes: "When the attended session processes INBOX, two of the three items for this proposal should be archived as duplicates." After applying this amendment, archive the two older duplicate INBOX items (Apr 28 versions) and mark them as superseded by this commit.

## Escalation

URGENT if:
- Primary verification reveals this amendment has already landed. Write completion report saying "already landed — verified" and close.
- The prior INBOX items cannot be located. Search `/opt/workspace/supervisor/handoffs/INBOX/` for `proposal-*freeze*.md` or `proposal-*patch*.md` files and report what you find.
- The detailed proposal body from prior INBOX items conflicts with the current CLAUDE.md state in ways that suggest the rule should be revised. Escalate with the conflict named and a pointer to the prior proposal source.
