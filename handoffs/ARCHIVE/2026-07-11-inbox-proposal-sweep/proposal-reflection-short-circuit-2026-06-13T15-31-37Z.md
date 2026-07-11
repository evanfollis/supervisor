---
from: synthesis-translator
to: general
date: 2026-06-13T15:31:37Z
priority: high
task_id: synthesis-p-reflection-short-circuit
source_synthesis: /opt/workspace/runtime/.meta/cross-cutting-2026-06-13T15-27-25Z.md
source_proposal: "Proposal 3 — P-reflection-short-circuit (3rd cycle, AT >3-CYCLE FLAG)"
---

# P-reflection-short-circuit

**Type:** Shared primitive amendment  
**File:** `supervisor/scripts/lib/reflect-prompt.md`  
**Target:** All projects (guidance + prompt template)  

## What

Formal guidance allowing reflections to degrade to single-paragraph status when all observations are unchanged for N=4 consecutive cycles. Context-repository has already self-degraded; this formalizes and standardizes the pattern.

**Proposed text (to add to reflect-prompt.md):**

```markdown
## Short-circuit rule

If ALL observations are unchanged for 4+ consecutive cycles, reduce to:

> **Short-circuit: cycle N.** M observations unchanged since [prior].
> Oldest unresolved: [item, age]. No new findings.

Resume full analysis when any observation changes status.
```

## Why

Signal exhaustion in an unclosed feedback loop. When observations repeat identically across cycles, producing full diagnostic output becomes noise — context-repository is already flagged at P3 with single-paragraph reflections, and skillfoundry-harness has explicitly noted exhausted escalation vocabulary.

Formalizing short-circuit mode:
- Standardizes a pattern already emerging organically
- Saves token budget across reflection loop (immediate, measurable)
- Prevents false "no signal" when suppression is actually the signal
- Aligns incentives: short reflections are honest (nothing new) vs. a full reflection that repeats identical findings (which appears as noise but is actually a cry for intervention)

**This pattern is at >3-cycle flag threshold.** Context-repository already proves it works.

## Verification before action

- [ ] Read `supervisor/scripts/lib/reflect-prompt.md` and confirm it does not already contain a short-circuit rule
- [ ] Check context-repository and skillfoundry-harness reflections to verify they have self-degraded (evidence the pattern is real and beneficial)
- [ ] Confirm the pattern is not documented elsewhere in supervisor/* that would conflict

## Acceptance criteria

- [ ] The short-circuit rule is added to `supervisor/scripts/lib/reflect-prompt.md` in a new `## Short-circuit rule` section
- [ ] Text is clear and prescriptive: N=4 consecutive cycles is the threshold, outcome is single-paragraph format, resumption condition is stated
- [ ] Change committed with message: "Add reflection short-circuit rule for exhausted observations (synthesis C96, P3)"
- [ ] No adversarial review required (guidance only, behavioral pattern formalization)
- [ ] Completion report at `runtime/.handoff/general-supervisor-synthesis-p-reflection-short-circuit-complete-<iso>.md`

## Escalation

**URGENT if:**
- The short-circuit rule is already in reflect-prompt.md. Write completion report: "Already documented at <line range>" and close.
- Verification reveals the pattern has already been formally reversed (a project has resumed full output despite >=4-cycle repetition). Investigate why before applying.
- The rule creates ambiguity about which observations count toward the "all unchanged" gate. Clarify before committing.

## Remarks

Guidance-only amendment (not enforcement). Context-repository has already self-degraded successfully. Token savings are immediate and measurable.
