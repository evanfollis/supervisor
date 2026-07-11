---
from: synthesis-translator
to: general
date: 2026-06-14T15:27:34Z
priority: medium
task_id: synthesis-reflection-short-circuit
source_synthesis: /opt/workspace/runtime/.meta/cross-cutting-2026-06-14T15-23-48Z.md
source_proposal: 4. P-reflection-short-circuit (carry from C94 — 5th cycle, PAST >3-CYCLE FLAG)
---

# P-reflection-short-circuit — Formalize observation-based short-circuit for reflections

## Proposal

Amend the reflection prompt (`supervisor/scripts/lib/reflect-prompt.md`) to add formal guidance allowing reflections to degrade to single-paragraph status when all observations are unchanged for N=4+ consecutive cycles.

This reduces diagnostic compute waste: currently 11 of 16 reflection sessions per cycle produce minimal signal, yet all run full analysis. Context-repository has already self-degraded to this pattern; formalizing the rule would make it systematic.

## Full proposal text from synthesis

**Type:** Shared primitive amendment.
**File:** `supervisor/scripts/lib/reflect-prompt.md`

**What:** Formal guidance allowing reflections to degrade to single-
paragraph status when all observations are unchanged for N=4 cycles.

**Sketch (unchanged):**
```markdown
## Short-circuit rule

If ALL observations are unchanged for 4+ consecutive cycles, reduce to:

> **Short-circuit: cycle N.** M observations unchanged since [prior].
> Oldest unresolved: [item, age]. No new findings.

Resume full analysis when any observation changes status.
```

**Blast radius:** All projects. Guidance only. Context-repository already
self-degraded to this pattern.

## Verification before action (required)

- Check `supervisor/scripts/lib/reflect-prompt.md` for existing short-circuit guidance.
- Verify whether the existing "Short-circuit rule" (activity-based) and the proposed rule (observation-based) should coexist or be merged.
- Review context-repository reflections to confirm the self-degradation pattern mentioned in the synthesis.

## Acceptance criteria

- A new observation-based short-circuit rule is added to `reflect-prompt.md` (or merged with existing short-circuit if appropriate).
- The rule is clear: "all observations unchanged for 4+ cycles → single-paragraph output".
- The rule includes guidance on what to include in the short-circuit paragraph (cycle number, observation count, oldest item, age).
- Resume conditions are explicit: full analysis resumes when any observation changes.
- Commit message explains the rationale (reduce wasted compute in steady-state periods).
- Adversarial review recommended to ensure the rule doesn't suppress valid diagnostic signals.

## Escalation

URGENT if:
- The existing activity-based short-circuit rule and the proposed observation-based rule would conflict. If so, propose a merged rule that handles both cases and ask for approval.
- Any reflection session is already ignoring this pattern despite needing it. Name the session and the issue.
