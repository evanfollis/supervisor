---
from: synthesis-translator
to: general
date: 2026-05-22T03:30:14Z
priority: high
task_id: synthesis-adr-0033-review
source_synthesis: /opt/workspace/runtime/.meta/cross-cutting-2026-05-22T03-23-17Z.md
source_proposal: Proposal 3 — ADR-0033 cross-agent review
---

# ADR-0033 cross-agent review

**Type:** Governance action.

**Change:** Commission a Claude or Codex session to review `supervisor/decisions/0033-passive-income-portfolio-abstraction.md` and produce an artifact at `supervisor/.reviews/adr-review-0033-<ts>.md`. Simultaneously confirm or correct the "decided by: principal" attribution.

**Rationale:** ADR-0033 is the most consequential governance output in weeks. It drove real strategy changes across four projects (atlas, skillfoundry-harness, skillfoundry-researcher, skillfoundry-valuation). However, it bypassed the charter's cross-agent review gate before acceptance. The charter requires adversarial review before accepting an ADR (CLAUDE.md §Review path). Additionally, the ADR claims "decided by: principal" but the authorship trail points entirely to agent sessions (Codex session `codex-2026-05-21-passive-income-portfolio`). No principal-written artifact or commit corroborates the decision attribution.

**Blast radius:** Supervisor repo only.

**Status:** Charter violation. The ADR is already shaping work across 4 projects. Late review is better than no review.

**ADR number recycling:** The same review session should scan tick-branch-proposed ADRs with:
```
git log --all --oneline -- 'decisions/0033-*'
```

Check whether the prior ADR-0033 (`0033-fr-allocation-main-branch-only.md` from tick-branch-proposed, commits `a316d7d`, `0f5f710`, `795ad7a`) still has value or can be archived. If dead, delete the branch copies to free the number cleanly. If still valuable, reserve the next free ADR number for the unmerged tick-branch ADR. This closes the recycling gap without a new process.

## Verification before action (required)

- Read `supervisor/decisions/0033-passive-income-portfolio-abstraction.md` to understand the ADR's scope and attribution claim.
- Check whether `supervisor/.reviews/adr-review-0033-*` already exists (if so, note the completion and close).
- Run `git log --all --oneline -- 'decisions/0033-*'` to identify any prior ADR-0033 usage and its status.

## Acceptance criteria

- A review artifact is produced at `supervisor/.reviews/adr-review-0033-<ts>.md` signed by the reviewing agent and including adversarial assessment of the ADR's decisions and consequences.
- The attribution question is resolved: either confirmed as principal-decided with corroborating evidence, or corrected to reflect agent authorship with principal acceptance noted.
- If the prior unmerged tick-branch ADR-0033 is dead, it is deleted and the number freed.
- If the prior ADR-0033 still has value, the next available ADR number is reserved and assigned to it via a new commit.
- Completion report at `runtime/.handoff/general-supervisor-adr-0033-review-complete-<iso>.md`.

## Escalation

URGENT if:
- The review identifies a material flaw in ADR-0033's reasoning that would cause projects to ship incorrect work. Escalate with the specific flaw and recommendation (revise the ADR, revert dependent changes, or proceed with documented risk).
- The attribution question reveals a governance gap that needs principal clarification (e.g. principal did accept ADR-0033 but it's not documented). Escalate with the specific question.
