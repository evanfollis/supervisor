# Escalation Contract

This document defines what should rise, what should stay local, and what an
acceptable escalation packet must contain.

## Escalation rule

Escalate only when the issue exceeds the current layer's delegated authority.

That normally means one of five things:

1. the issue is novel and there is no stable local policy
2. the issue crosses project boundaries
3. the issue changes architecture or authority allocation
4. the issue has meaningful blast radius or irreversible consequences
5. the issue remains ambiguous after local compression effort

## Layer-to-layer rules

### Project agent → project manager

Escalate when:

- a task needs policy interpretation, not just execution
- repeated local failures suggest workflow drift
- the task touches shared project invariants
- the task appears to require repo-level or process-level change

Do not escalate:

- routine implementation decisions already covered by project policy
- reversible experimentation inside delegated scope

### Project manager → workspace supervisor

Escalate when:

- the issue affects multiple repos or shared infrastructure
- the project needs a new workspace-level policy or carve-out
- repeated local friction appears across more than one project
- the project manager cannot resolve the issue without reinterpreting the
  workspace contract

Do not escalate:

- project-local implementation details
- one-off issues that can be solved by local policy

### Workspace supervisor → human principal

Escalate when:

- policy must change
- authority boundaries must expand or contract
- the issue is strategically consequential
- a conflict exists between existing policies
- the workspace lacks enough clarity to govern safely

Do not escalate:

- routine routing and triage
- repeated issues that can be codified into supervisor playbooks or ADRs

## Escalation packet

Every escalation should be small, explicit, and auditable. The minimum packet:

- `intent_model` or concise problem framing
- `task_id`
- `who_escalated`
- `from_layer`
- `to_layer`
- `scope`
- `objective`
- `constraints`
- `non_goals`
- `decision_needed`
- `why_local_policy_failed`
- `evidence`
- `options_considered`
- `recommended_path`
- `deadline_or_urgency`

## Downward policy packet

When a higher layer resolves an escalation, the response should be packaged so
it can move downward without reinterpretation.

Minimum fields:

- `policy_change`
- `applies_to`
- `effective_from`
- `reason`
- `examples`
- `rollback_or_exception_rule`

## Anti-patterns

Reject these forms of escalation:

- transcript dumps with no stated decision need
- vague "please advise" routing
- escalations that hide what was already tried
- escalations motivated by convenience rather than authority boundaries

The supervisor should compress these before passing them upward.

## Cross-runtime result packet

When a lower runtime completes delegated work, the return packet should contain:

- `task_id`
- `status`
- the receiver's understanding of what the task was really trying to achieve
- summary of work performed
- changed artifacts or outputs
- validations performed
- assumptions made
- shortcuts taken
- unresolved risks
- follow-up recommendations
- explicit escalation items, if any
