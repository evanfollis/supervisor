---
from: synthesis-translator
to: general-codex
date: 2026-07-20T09:38:15Z
priority: high
task_id: synthesis-primary-object-witness-for-prescriptions
source_synthesis: /opt/workspace/runtime/.meta/cross-cutting-2026-07-20T09-33-26Z.md
source_proposal: 4. CLAUDE.md amendment — primary-object witness for prescriptions
authority: synthesis proposal under ADR-0020 reversible-action scope
external_dependencies: none
policy_compatibility: verified against matching accepted Decisions; no conflict found
---

# CLAUDE.md amendment — primary-object witness for prescriptions

**Section:** `Quality: Root-Cause Discipline`, after “Read primary evidence literally before theorizing.”

Exact delta:

> **A prescriptive artifact must carry a witness to its primary object.** Before a reflection, CURRENT_STATE file, completion report, or CI result promotes a concrete instruction or “passing” claim, verify the referenced symbol/path exists, the intended runner actually collects the relevant tests/cases, and any reported live state was freshly measured. If the current harness cannot perform that check, label the item `UNVERIFIED` and keep it conjectural; do not serialize it as an executable NEXT action. A green command proves only what it demonstrably collected and exercised.

**Blast radius:** All workspace projects and agents; automatic as instruction, with hard enforcement supplied by Proposals 2 and 3 where supported.

## Verification before action (required)

- Run `git log --oneline -20` on the target repo. Check if this proposal has already landed via another path.
- Read the target file. Check if the specified state is already present.
- If either is true, write a completion report stating "already landed at commit <SHA> / verified in-file" rather than re-applying.

## Acceptance criteria

- The patch specified in the synthesis is applied (or verified already applied).
- Change committed with clear message explaining the synthesis source.
- Adversarial review via `supervisor/scripts/lib/adversarial-review.sh` when the proposal is non-trivial (structural changes, multi-file edits, schema bumps).
- Completion report at `runtime/.handoff/general-<target>-synthesis-<slug>-complete-<iso>.md` pointing back to this handoff and the source synthesis.

## Escalation

URGENT if:
- Primary verification reveals the proposal is based on stale state (synthesis ran pre-fix; the fix landed by another path between synthesis run and this handoff write). Write a brief completion report saying "obsolete — already landed" and close.
- The proposal conflicts with a more recent decision. Do not force-apply; escalate with the conflict named.
- The proposal requires principal input the translator missed (people-or-money rubric was misapplied). Surface the specific person or dollar figure.
