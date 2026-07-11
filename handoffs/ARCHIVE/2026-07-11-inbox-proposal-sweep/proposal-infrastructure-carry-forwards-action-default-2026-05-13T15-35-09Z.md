---
from: synthesis-translator
to: general
date: 2026-05-13T15:35:09Z
priority: high
task_id: synthesis-proposal-3-infra-action-default
source_synthesis: /opt/workspace/runtime/.meta/cross-cutting-2026-05-13T15-26-05Z.md
source_proposal: "Proposal 3 — Infrastructure carry-forwards eligible for project-local resolution"
---

# Amend CLAUDE.md: Infrastructure carry-forwards may be resolved by project sessions

## Summary

Cycle 34 observations show that infrastructure carry-forwards resolved via project-local action (synaplex CURRENT_STATE.md) arrived faster and cleaner than those routed through the executive queue (0-for-8 unconsumed). The difference is routing: operational carry-forwards (not strategic) can be shipped by project sessions under action-default scope, bypassing the executive queue entirely. This proposal amends workspace CLAUDE.md to codify this pattern.

## The fix

Add the following bullet to `/opt/workspace/CLAUDE.md` under the **Active Decisions → Agent Behavior** section (after the existing action-default bullet):

```markdown
### Infrastructure carry-forwards with project-local fixes may be resolved by project sessions under action-default scope

If a carry-forward item (a) has been proposed for 3+ reflection cycles, 
(b) has a known fix that does not require a workspace-wide trust 
decision or new external credentials, and (c) affects primarily the 
project where the session is running, the project session should ship the 
fix rather than routing it through the executive queue. The completion 
handoff to the executive records what was done and why. This does not 
apply to changes that modify shared infrastructure (`supervisor/scripts/lib/`), 
grant new authority, or affect other projects' behavior.
```

This should be inserted after the existing "Action-default contract (ADR-0020)" bullet to clarify scope for infrastructure work.

## Why this works

- **Evidence-backed:** The synaplex CURRENT_STATE.md resolution (commits `808ee8c`, `44deac1`, `5f4f7c7`) shipped within the same reflection cycle using this approach. Compare: executive-queued infrastructure items are 0-for-8 and have waited 22–277 hours unconsumed.
- **Operational distinction:** Strategic decisions (grant new authority, policy changes across projects) still route through the executive. Operational fixes (local CLAUDE.md amendments, committed state cleanup, project-scoped bug fixes) can ship immediately.
- **Preserves control plane separation:** The executive is not bypassed; it receives completion handoffs that record what was done and the decision rationale. The queue is just not used as a bottleneck for work the project session can own.
- **Replicable:** The same pattern applies to context-repository (CURRENT_STATE.md drift) and skillfoundry-harness (12-cycle gap) — both are operational, local, and ready to ship with project authority alone.

## Verification before action (required)

- Read `/opt/workspace/CLAUDE.md` at the **Active Decisions → Agent Behavior** section. Verify the existing "Action-default contract (ADR-0020)" bullet is present.
- Check if infrastructure-carry-forward language is already present in CLAUDE.md (if so, compare to the proposal and report whether it matches or supersedes).
- Confirm the rule does not conflict with any standing principal decision (check supervisor/decisions/).

## Acceptance criteria

- New bullet added to Agent Behavior section verbatim or with minor clarification.
- Placement immediately after or integrated with the existing ADR-0020 action-default bullet to maintain coherence.
- Commit with a message explaining the synthesis source (e.g., "Codify infrastructure carry-forward resolution path; enable project-local action-default per synthesis cycle 34").
- Completion report confirms rule landed and notes that context-repository and skillfoundry-harness are now eligible to adopt Option B (CURRENT_STATE.md discipline) under this authority.

## Escalation

URGENT if:
- The existing action-default language in CLAUDE.md has changed significantly since this proposal was written (review recent commits).
- A principal decision exists that contradicts project-local infrastructure authority (check supervisor/decisions/); if so, flag the conflict rather than force-applying.
- The rule language conflicts with any standing governance in supervisor/ (check system/status.md, active-issues.md).
