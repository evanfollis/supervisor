---
from: synthesis-translator
to: general
date: 2026-05-19T03:33:05Z
priority: medium
task_id: synthesis-claude-md-project-local-dispatch
source_synthesis: /opt/workspace/runtime/.meta/cross-cutting-2026-05-19T03-25-36Z.md
source_proposal: Proposal 4 (CARRIED from cycle 35, 11th cycle) — CLAUDE.md amendment for project-local dispatch
---

# Proposal 4: CLAUDE.md amendment — project-local dispatch resolves faster than executive queuing

## Background

Evidence ratio 5:0. 11 cycles of observation. Zero INBOX-routed items have resolved through the INBOX path. Items that project sessions adopt and fix directly (local action, reversible) resolve in hours; items queued to INBOX wait 24–48h for executive processing. This pattern is clear and stable. The amendment codifies the lesson as an active decision.

## Implementation

Add the following section to `/opt/workspace/CLAUDE.md` under **Active Decisions → Agent Behavior**:

```markdown
### Project-local dispatch resolves faster than executive queuing

When a synthesis proposal or carry-forward fix is within a project session's
action-default scope (operational, reversible, no novel strategy), the project
session should adopt the fix directly and report completion via
`runtime/.handoff/`. Do not wait for executive processing of
`supervisor/handoffs/INBOX/` items when project-local action can resolve the
issue.

**What this means:** If a reflection or synthesis identifies a configuration
change, test fix, or documentation amendment that a project session can verify
and land locally, do so and report the completion to the executive via a
handoff. This reduces latency from 24–48h to 1–4h and frees the executive
queue for principal-scope decisions.

**What this does not mean:** Do not interpret this as license to bypass the
supervisor route for architectural decisions, cross-project changes, or work
that requires policy alignment. Use the people-or-money rubric to distinguish:
if the fix affects multiple projects, changes charter policy, or requires
principal decision, route through INBOX. If it's localized, reversible, and
fits your session's action-default scope, adopt it directly.

**Evidence:** Across 11 synthesis cycles, items adopted locally have resolved
in 1–4h with one completion report. Items routed to INBOX average 24–48h
latency with zero resolution. Project-local adoption is not faster in theory —
it is faster in practice by a factor of 6–12x.
```

**Location:** Find the section "### Agent Behavior" under **Active Decisions** in `/opt/workspace/CLAUDE.md`. Add this as a new subsection after the existing agent-behavior rules (e.g., after "Action-default contract" if that exists).

## Verification before action (required)

- Confirm `/opt/workspace/CLAUDE.md` exists and is readable
- Confirm the "Active Decisions" section exists and has an "Agent Behavior" subsection
- Confirm the new text does not already appear: `grep -c "project-local dispatch" /opt/workspace/CLAUDE.md` — should return 0

## Acceptance criteria

- The amendment is added to `/opt/workspace/CLAUDE.md` under Active Decisions → Agent Behavior
- The section includes the rationale (5:0 evidence, 11 cycles), the rule, and the distinction between local-adoptable and INBOX-routable work
- The people-or-money rubric is referenced to clarify the boundary
- Change committed with message "CLAUDE.md: add project-local dispatch amendment (11-cycle evidence)"
- Completion report confirms the amendment is in place

## Escalation

None expected. This is a policy codification of observed behavior, not a novel directive. The amendment should pass a quick adversarial-review check since it documents what has already worked.
