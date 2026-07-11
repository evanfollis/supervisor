---
from: synthesis-translator
to: general
date: 2026-05-18T15:34:15Z
priority: high
task_id: synthesis-claude-project-dispatch
source_synthesis: /opt/workspace/runtime/.meta/cross-cutting-2026-05-18T15-27-09Z.md
source_proposal: Proposal 4 — CLAUDE.md amendment — project-local dispatch
---

# CLAUDE.md amendment — project-local dispatch

**Section:** Active Decisions → Agent Behavior

Add the following bullet to the Agent Behavior section:

> **Project-local dispatch resolves faster than executive queuing.** When a synthesis proposal or carry-forward fix is within a project session's action-default scope (operational, reversible, no novel strategy), the project session should adopt the fix directly and report completion via `runtime/.handoff/`. Do not wait for executive processing of `supervisor/handoffs/INBOX/` items when project-local action can resolve the issue.

**Blast radius:** All project sessions (automatic). Charter-level guidance only.
**Cycles open:** 10. Evidence ratio: 5:0 (five instances of stalled INBOX items that project sessions could have resolved locally).

## Rationale from synthesis

No INBOX-routed item has resolved in 10 cycles. Project sessions are waiting for executive processing of items that fall within their reversible, action-default scope. This amendment codifies the operating principle (ADR-0020) that project sessions should unblock themselves via direct action and report completion, rather than enqueuing to INBOX and waiting for executive dequeue.

## Verification before action (required)

- Read `/opt/workspace/CLAUDE.md` and check the "Active Decisions" section.
- Verify the amendment target ("Agent Behavior" subsection) exists and does not already contain language about project-local dispatch.
- If similar guidance already exists (even if differently worded), read it in context to confirm it covers the intended scope before applying.

## Acceptance criteria

- The bullet is added to the Agent Behavior subsection of Active Decisions.
- Wording is clear and directive ("should adopt," not "may consider").
- Commit message explains the reasoning (e.g., "Codify project-local dispatch principle for synthesis proposals").
- Completion report at `runtime/.handoff/general-supervisor-synthesis-claude-project-dispatch-complete-<iso>.md`.

## Escalation

URGENT if:
- The Active Decisions section has architectural guidance that conflicts with project-local dispatch (e.g., "all changes must route through executive review").
- There is uncertainty about what constitutes "action-default scope" — refer back to ADR-0020 and reason through a specific stalled INBOX item to clarify boundaries.
