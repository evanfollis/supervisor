---
from: synthesis-translator
to: general
date: 2026-06-15T15:34:28Z
priority: medium
task_id: synthesis-p-reflection-short-circuit
source_synthesis: /opt/workspace/runtime/.meta/cross-cutting-2026-06-15T15-26-25Z.md
source_proposal: "Proposal 4 — P-reflection-short-circuit (carry from C94 — 7th cycle, PAST >3-CYCLE FLAG)"
---

# P-reflection-short-circuit

**Type:** Shared primitive amendment.
**File:** `supervisor/scripts/lib/reflect-prompt.md`

## Problem

Reflection sessions fire on a fixed 12-hour schedule regardless of activity. When all observations are unchanged for 4+ cycles, full-text reflections become diagnostic noise — documenting steady state rather than surfacing new signal.

Context-repository has already self-degraded to single-paragraph status (see synthesis Pattern 4). This rule formalizes that pattern across all projects.

## Solution

Add formal guidance allowing reflections to degrade to single-paragraph status when all observations are unchanged for N=4 cycles.

Add this section to `supervisor/scripts/lib/reflect-prompt.md`:

```markdown
## Short-circuit rule

If ALL observations are unchanged for 4+ consecutive cycles, reduce to:

> **Short-circuit: cycle N.** M observations unchanged since [prior].
> Oldest unresolved: [item, age]. No new findings.

Resume full analysis when any observation changes status.
```

## Verification before action (required)

- Read `supervisor/scripts/lib/reflect-prompt.md` and check if the "Short-circuit rule" section already exists.
- If it does, verify the rule allows short-circuit format after 4 unchanged cycles.
- If already present, write a completion report stating "already landed" rather than re-applying.

## Acceptance criteria

- The "Short-circuit rule" section is added to `reflect-prompt.md`.
- The rule clearly states the N=4 cycle threshold.
- The rule specifies the minimal single-paragraph format.
- Change committed with clear message: "Formalize reflection short-circuit rule for steady-state projects (synthesis C100, Proposal 4)".

## Escalation

URGENT if:
- Primary verification shows the rule is already in place. Write completion report stating "already landed" and close.
- The 4-cycle threshold conflicts with project-specific guidance. Escalate with the conflict named.

---

## Notes from synthesis

- Carried from C94 (7th cycle) — past the >3-cycle flag.
- Context-repository has already adopted this pattern informally.
- Guidance-only change, zero risk.
- Affects all projects by reducing noise in steady-state phases.
