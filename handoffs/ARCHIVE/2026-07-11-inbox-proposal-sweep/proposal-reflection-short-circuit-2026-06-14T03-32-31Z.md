---
from: synthesis-translator
to: general
date: 2026-06-14T03:32:31Z
priority: medium
task_id: synthesis-reflection-short-circuit
source_synthesis: /opt/workspace/runtime/.meta/cross-cutting-2026-06-14T03-27-39Z.md
source_proposal: 4. P-reflection-short-circuit (carry from C94 — 4th cycle, PAST >3-CYCLE FLAG)
---

# P-reflection-short-circuit — Formalize observation degradation rule

## Proposal

**Type:** Shared primitive amendment.  
**File:** `supervisor/scripts/lib/reflect-prompt.md`

**What:** Formal guidance allowing reflections to degrade to single-paragraph status when all observations are unchanged for N=4 consecutive cycles. Context-repository has already self-degraded to this pattern in recent cycles; this proposal formalizes and standardizes it.

**Proposed amendment:**

Add a new section to `reflect-prompt.md` after the existing "Short-circuit rule":

```markdown
## Observation degradation rule

If ALL observations from the prior reflection are unchanged for 4+ consecutive cycles (no new findings, no state changes, same blockers), reduce this cycle's output to:

> **Observation degradation: cycle N.** M observations unchanged since [prior cycle date].
> Oldest unresolved: [item, age]. No new findings this window.

Do not re-expand to full analysis until an observation changes status or a new finding emerges.

This rule saves context and prevents identical repetition while preserving the signal that nothing has changed.
```

**Blast radius:** All projects. Guidance only (not enforcement). Token savings are immediate — context-repository already proves the pattern works. Low risk.

## Rationale

When a project's reflection generates identical findings across multiple cycles (typically due to unresolved blockers or awaiting external action), the full reflection output becomes redundant. This rule permits degradation to a single-line status, freeing context for projects with active discovery. The synthesis job can still read and aggregate these degraded reflections.

## Verification before action (required)

- [VERIFIED] `supervisor/scripts/lib/reflect-prompt.md` does not contain an "Observation degradation rule" section.
- Context-repository's recent reflections show manual use of this pattern.
- This proposal has not been landed by another path.

## Acceptance criteria

- A new "## Observation degradation rule" section is added to `reflect-prompt.md` with guidance for N=4 consecutive unchanged cycles.
- The section appears after the "Short-circuit rule" section (or the "Action routing rule" if P-reflect-route-known-fixes lands first).
- Change committed with a message citing the synthesis source.
- No adversarial review needed (prompt guidance only).
- Completion report at `runtime/.handoff/general-supervisor-synthesis-degradation-complete-<iso>.md` pointing back to this handoff.

## Escalation

URGENT if:
- The amendment appears to have already landed.
- The current state of the file contradicts what is described here.
