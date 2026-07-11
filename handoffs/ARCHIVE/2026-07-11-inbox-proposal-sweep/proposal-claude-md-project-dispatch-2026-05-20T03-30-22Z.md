---
from: synthesis-translator
to: general
date: 2026-05-20T03:30:22Z
priority: medium
task_id: synthesis-claude-md-project-dispatch
source_synthesis: /opt/workspace/runtime/.meta/cross-cutting-2026-05-20T03-25-45Z.md
source_proposal: "Proposal 4 (MEDIUM — 13th cycle): CLAUDE.md amendment — project-local dispatch"
---

# CLAUDE.md amendment — project-local dispatch

## Context

Over 13 synthesis cycles, zero INBOX-routed dispatch items have resolved through the INBOX path. The evidence ratio is 5:0 — all observed dispatch issues involve the INBOX queue, not the downstream project work. This suggests that project sessions are uncertain about whether they should dispatch work locally or route through INBOX, and the charter guidance needs clarification.

The synthesis proposes an amendment to clarify when project sessions should dispatch locally vs. escalate to INBOX.

## The Fix

**File**: `/opt/workspace/CLAUDE.md`, section "Active Decisions → Agent Behavior"
**Target**: Add a rule clarifying project-local dispatch authority

Proposed amendment (sketch from cycle 46):

```markdown
- **Project sessions dispatch locally by default.** A project session should emit handoffs to the executive (`runtime/.handoff/general-<project>-*.md`) only for items that require principal decision (novel strategy, irreversible external commitments, legal scope) or cross-project coordination. For project-local work — feature sessions, PM sessions within the project, tooling fixes — the project session owns dispatch authority. The INBOX is for workspace-level governance and cross-project synthesis, not for within-project task routing. This inverts the current pattern of all work queuing through INBOX.
```

**Rationale**: Project sessions have been over-escalating to INBOX because the charter doesn't distinguish between "project session dispatch to project-local work" and "escalation to the executive." This amendment makes that distinction explicit.

## Blast Radius

- CLAUDE.md amendment only (guidance/policy, no code change)
- Affects all project sessions (automatic, next session launch)
- Should increase project autonomy and reduce INBOX churn
- Clarifies existing ADR-0020 intent without changing it

## Cycles open

- 13 cycles as synthesis proposal
- Zero resolved dispatch items through current INBOX path over 13 cycles

## Verification before action (required)

- Read `/opt/workspace/CLAUDE.md` at the "Active Decisions → Agent Behavior" section (around line 124)
- Confirm the amendment is not already present
- Check if ADR-0020 (`supervisor/decisions/0020-action-default-contract-across-agents.md`) exists and conflicts with the proposed amendment
- If ADR-0020 contradicts the amendment, escalate with the specific conflict named

## Acceptance criteria

- The amendment is added to the "Agent Behavior" subsection of "Active Decisions"
- Wording distinguishes project-local dispatch (project session authority) from escalation (executive authority)
- Commit message explains the 13-cycle evidence and the intent to increase project autonomy
- Change is reviewed in-session or routed to `/review` if substantive charter change
- Completion report at `runtime/.handoff/general-supervisor-synthesis-claude-md-amendment-complete-<iso>.md`

## Escalation

URGENT if:
- ADR-0020 and the proposed amendment conflict — escalate with both documents cited
- The amendment is already present (landed by another path between synthesis and now)
- Principal has stated a different dispatch model in recent messages (check JSONL user turns for contradicting guidance)
