---
from: synthesis-translator
to: general
date: 2026-06-16T03:28:14Z
priority: high
task_id: synthesis-reflection-short-circuit
source_synthesis: /opt/workspace/runtime/.meta/cross-cutting-2026-06-16T03-23-07Z.md
source_proposal: 3. P-reflection-short-circuit (carry from C94 — 8th cycle, PAST >3-CYCLE FLAG)
---

# P-reflection-short-circuit

**Type:** Shared primitive amendment.
**File:** `supervisor/scripts/lib/reflect-prompt.md`

**What:** Formal guidance allowing reflections to degrade to single-paragraph status when all observations are unchanged for N=4 cycles.

**Sketch (unchanged):**
```markdown
## Short-circuit rule

If ALL observations are unchanged for 4+ consecutive cycles, reduce to:

> **Short-circuit: cycle N.** M observations unchanged since [prior].
> Oldest unresolved: [item, age]. No new findings.

Resume full analysis when any observation changes status.
```

**Blast radius:** All projects. Guidance only. Context-repository already self-degraded to this pattern.

## Background

This proposal has been carried for 8 cycles. It addresses a pattern where reflections remain mechanically identical from cycle to cycle, producing ~85 diagnostic artifacts per genuinely new finding. Formal short-circuit guidance allows reflections to degrade gracefully when the state is stale, reducing noise without losing signal.

## Verification before action (required)

- Run `git log --oneline -20` on `/opt/workspace/supervisor`. Check if this proposal has already landed via a commit adding the short-circuit rule to reflect-prompt.md.
- Read `supervisor/scripts/lib/reflect-prompt.md`. Check if a "Short-circuit rule" or similar section already exists with the N=4-cycle guidance.
- If either check shows the guidance is already in place, write a completion report stating "already landed at commit <SHA>" rather than re-applying.

## Acceptance criteria

- Short-circuit rule section added to `supervisor/scripts/lib/reflect-prompt.md` with clear guidance on when to apply it (N=4+ cycles, all observations unchanged).
- Rule includes guidance on what a short-circuit report looks like and when to resume full analysis.
- Change committed with a message explaining the motivation (reduce diagnostic noise from stale observations).
- Completion report at `supervisor/handoffs/ARCHIVE/<iso>/general-reflection-short-circuit-complete.md` pointing back to this handoff and the source synthesis.

## Escalation

URGENT if:
- Verification reveals the guidance is already in place. Write a brief completion report and close.
- The reflect-prompt.md file has structural changes that make the proposed addition conflict. Detail the conflict.
