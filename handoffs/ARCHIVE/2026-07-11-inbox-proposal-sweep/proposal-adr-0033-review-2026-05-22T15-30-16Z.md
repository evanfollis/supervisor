---
from: synthesis-translator
to: general
date: 2026-05-22T15:30:16Z
priority: high
task_id: synthesis-adr-0033-cross-review
source_synthesis: /opt/workspace/runtime/.meta/cross-cutting-2026-05-22T15-24-17Z.md
source_proposal: Proposal 3 (HIGH — 2nd cycle)
---

# Commission ADR-0033 cross-agent review

## Summary

ADR-0033 ("Passive Income Portfolio Abstraction") exists at `supervisor/decisions/0033-passive-income-portfolio-abstraction.md` but lacks cross-agent review. The ADR states "decided by: principal" but no evidence of principal sign-off is available (no ".reviews/" file). The ADR is shaping work across 4 projects (atlas, skillfoundry projects) without having been adversarially reviewed. Two synthesis cycles have flagged this.

Additionally, there is a prior branch-level ADR-0033 artifact (`0033-fr-allocation-main-branch-only.md`) that needs to be resolved to prevent ADR number recycling.

## The work

1. **Adversarial review of ADR-0033**: Route to any Claude session with review authority (preferably the opposing agent). Produce `.reviews/adr-review-0033-<timestamp>.md` with:
   - Assessment of the decision's coherence
   - Identification of any assumptions that may be fragile
   - Verification that "decided by: principal" attribution is correct (check `/root/.claude/projects/-opt-workspace/*.jsonl` for Evan's explicit approval, or check `decisions/` for a prior decision that subsumes this)
   - Recommendations for any amendments or dependencies

2. **Resolve ADR number collision**: Verify and document the relationship between `0033-passive-income-portfolio-abstraction.md` (current) and `0033-fr-allocation-main-branch-only.md` (tick-branch artifact). Either:
   - Confirm the older artifact is superseded and can be discarded
   - If both are live, reorder one to use the next available ADR number and update references

3. **Attribution verification**: If the review confirms principal sign-off is missing, update the ADR's "decided by:" field or escalate for explicit approval.

## Impact

- Affected: `supervisor/decisions/0033-*` files and any `.reviews/` directory
- Blast radius: Governance transparency only. No code changes; no deployed systems.
- Side effect: Clarified decision provenance may change how the ADR is prioritized or amended, but the decision itself does not change during review.

## Verification before action

- Run `ls -la supervisor/decisions/0033* supervisor/.reviews/adr-review-0033*` and confirm the review file does not exist.
- Read `supervisor/decisions/0033-passive-income-portfolio-abstraction.md` and note the "decided by:" and "status:" fields.
- Grep the most recent JSONL session transcripts (`/root/.claude/projects/-opt-workspace-*.jsonl`) for Evan's explicit approval of this ADR. If found, note the date and session name.
- If review file doesn't exist and decision is live, proceed with review.

## Acceptance criteria

- A cross-agent review is commissioned (e.g., `supervisor/scripts/lib/adversarial-review.sh` is called with the ADR as input, or a manual prompt is sent to an opposing-agent session).
- Review output is written to `supervisor/.reviews/adr-review-0033-<timestamp>.md` with:
  - Coherence assessment
  - Assumption inventory
  - Attribution verification result
  - Recommendations (if any)
- ADR number collision is resolved (confirm tick-branch artifact status; reorder if needed).
- Commit message (imperative): "Review ADR-0033 and resolve attribution — cross-agent review and decision verification"
- Escalation to principal only if review identifies a structural problem (conflicting assumptions, missing approval, or a decision that contradicts workspace charter).

## Escalation

URGENT if:
- Review reveals "decided by: principal" is false (principal never explicitly approved). Escalate for sign-off or amendment.
- Review identifies conflicts with existing decisions or charter. Escalate for resolution before marking ADR accepted.
- ADR number collision cannot be cleanly resolved (both artifacts are live and non-redundant). Escalate for manual arbitration.
