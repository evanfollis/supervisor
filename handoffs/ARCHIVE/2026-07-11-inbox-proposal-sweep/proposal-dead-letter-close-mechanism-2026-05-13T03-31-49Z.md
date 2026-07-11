---
from: synthesis-translator
to: general
date: 2026-05-13T03:31:49Z
priority: high
task_id: synthesis-dead-letter-close-mechanism
source_synthesis: /opt/workspace/runtime/.meta/cross-cutting-2026-05-13T03-25-55Z.md
source_proposal: Proposal 3 — Dead-letter close mechanism
---

# Dead-letter close mechanism

## Summary

Unchanged from cycle-32 P5. Multiple projects carry items that are trivially fixable, confirmed false, or past any reasonable carry-forward budget — yet no mechanism closes them. The reflection loop faithfully re-states them every 12h, spending observation slots on items that are scheduling failures, not hard problems.

This proposal establishes a force-close rule: items carried for 5 consecutive reflection cycles without resolution must be explicitly disposed (won't-fix, confirmed-false, etc.) or escalated.

## Evidence (current)

- **SF-harness**: `tests/conftest.py:52` — 7 consecutive cycles (was 6 in cycle 32), no new rationale for deferral.
- **Command**: Login double-submission carry-forward — **20+ days**, every reflection since 2026-04-24.
- **Context-repo**: `docs/polarity-schema-v0.1.1-audit.md` — 21 days ungated, "waiting for adversarial review" is now an abandoned proposal.
- **Supervisor**: `active-issues.md` sourceType entry is confirmed stale. The tick at 14:47Z had Tier-A authority to close it but did not — evidence the gap extends below the attended-session layer.

## Proposed CLAUDE.md amendment

Target file: `/opt/workspace/CLAUDE.md` § Quality: Radical Truth

Add a new bullet:

```
**Carry-forward items must resolve, close, or escalate by their 5th
reflection cycle.** An item carried for 5 consecutive cycles without
a code fix, a recorded deferral in `supervisor/decisions/`, or a
format-escalation (INBOX → handoff) must be force-closed with a
`won't-fix` or `confirmed-false` disposition. The disposition must
state why the item persisted and whether the persistence itself
reveals a structural gap. Perpetual carry-forward is not a resolution
path — it is attention debt that degrades the signal quality of every
subsequent reflection.
```

## Rationale (from synthesis)

The reflection loop has no force-close or dead-letter mechanism. Items below the attended-session's attention threshold persist indefinitely, consuming observation bandwidth that could surface genuinely new problems. The carry-forward list becomes noise, which further reduces the probability any individual item gets attention — a vicious cycle.

This rule breaks that cycle by forcing explicit disposition at the 5-cycle boundary.

## Implementation (notes)

This amendment affects:
- Reflection prompts in all projects (must adopt the rule in reflect-prompt.md)
- Supervisor reflection (must apply the rule to active-issues.md and similar governance artifacts)

The rule is opt-in — projects adopt it incrementally. No retroactive cleanup required; the rule applies to cycles after deployment.

## Verification before action (required)

- Run `git log --oneline -20` on supervisor. Check if this amendment has landed via another path.
- Read `/opt/workspace/CLAUDE.md` § Quality: Radical Truth. Verify the text is not already present.
- If either is true, write a completion report stating "already landed at commit <SHA> / verified in-file" rather than re-applying.

## Acceptance criteria

- The amendment (exact text above) is inserted into `/opt/workspace/CLAUDE.md` § Quality: Radical Truth.
- Change committed with clear message explaining the synthesis source and rationale.
- Completion report at `/opt/workspace/runtime/.handoff/general-general-dead-letter-close-mechanism-complete-<iso>.md` pointing back to this handoff and the source synthesis.

## Escalation

URGENT if:
- The amendment conflicts with a more recent decision in `/opt/workspace/supervisor/decisions/`. Do not force-apply; surface the conflict.
- `/opt/workspace/CLAUDE.md` § Quality: Radical Truth structure differs from what the proposal assumes. Report the mismatch and ask for clarification on where to place the text.
