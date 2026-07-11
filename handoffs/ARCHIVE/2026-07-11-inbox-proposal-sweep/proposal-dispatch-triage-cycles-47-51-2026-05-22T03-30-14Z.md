---
from: synthesis-translator
to: general
date: 2026-05-22T03:30:14Z
priority: medium
task_id: synthesis-dispatch-triage-47-51
source_synthesis: /opt/workspace/runtime/.meta/cross-cutting-2026-05-22T03-23-17Z.md
source_proposal: Proposal 4 — Resolve dispatch handoff accumulation (cycles 47–51)
---

# Resolve dispatch handoff accumulation (cycles 47–51)

**Type:** Queue triage.

**Action:** The general session (as executive) must determine: did ADR-0033 implicitly address the intent of cycles 47–49? Based on that determination:

- **If yes:** Archive those 3 handoffs with a note referencing ADR-0033 (move to `handoffs/ARCHIVE/2026-05/`).
- **If no:** Dispatch them via new handoffs to the intended target sessions.
- Either way, record the decision in a triage report.

Cycles 50–51 handoffs are within the 24h SLA and should be dispatched or deferred normally (not affected by this triage).

**Rationale:** Three handoffs from cycles 47–49 are past the 24h dispatch SLA with no deferral recorded. The ambiguity (whether ADR-0033 resolved their intent) is the core problem — carrying forward an ambiguous item adds no value. A triage decision closes the loop cleanly.

**Blast radius:** `runtime/.handoff/general-synthesis-cycle47-51-*.md` and archive operations only.

**Status:** Three handoffs past 24h SLA with no deferral. The ambiguity is the problem.

## Verification before action (required)

- List current handoffs: `ls /opt/workspace/runtime/.handoff/general-synthesis-cycle47-*.md` to identify which ones exist.
- Read each handoff to understand its original intent.
- Read `supervisor/decisions/0033-passive-income-portfolio-abstraction.md` to understand ADR-0033's scope.
- Determine whether ADR-0033 logically addressed the intent of cycles 47–49.

## Acceptance criteria

- A triage decision is recorded in `runtime/.handoff/general-supervisor-dispatch-triage-47-51-<iso>.md` stating whether each cycle-47–49 handoff was addressed by ADR-0033.
- Handoffs determined to be addressed by ADR-0033 are moved to `handoffs/ARCHIVE/2026-05/` with a note: "Addressed by ADR-0033 (supervisor decision, <date>)".
- Handoffs determined to NOT be addressed by ADR-0033 are re-dispatched to their target sessions with a note that they were held pending ADR-0033 and should now proceed.
- Cycles 50–51 handoffs are inspected and either dispatched or deferred with explicit reasoning.
- Completion report at `runtime/.handoff/general-supervisor-dispatch-triage-complete-<iso>.md`.

## Escalation

URGENT if:
- ADR-0033 and cycles 47–49 handoffs are in fundamental tension (ADR-0033 resolves the intent but changes the approach significantly). Note the conflict and recommend whether to supersede the old handoffs or reconcile them.
- The triage decision requires principal judgment beyond what ADR-0033 states (e.g. "ADR-0033 partially addressed intent but left gaps"). Escalate with the specific gaps and ask whether to proceed anyway or dispatch with modified scope.
