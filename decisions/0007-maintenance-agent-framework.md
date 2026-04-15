# ADR-0007: Explicit maintenance-agent framework with shared skills

Date: 2026-04-14
Status: accepted

## Context

The workspace now has a clean recursive delegation model, a novelty ledger, and
an active idea-focus queue. The next structural risk is predictable:

- if the supervisor absorbs every maintenance concern itself, it becomes a
  synchronous bottleneck
- if maintenance work is spun up ad hoc around immediate pain points, the
  system will drift into overweighted dual-role loops that are hard to unwind
  later

The requirement is to preserve a clean future shape now, before operational
bloat narrows the available design space.

## Decision

Define an explicit **maintenance-agent framework** now, even if most roles
remain inactive at first.

The framework has two parts:

1. **Maintenance agents** under `supervisor/maintenance-agents/`
   - durable role manifests
   - narrow scoped responsibilities
   - explicit inputs, outputs, cadence, and escalation rules

2. **Shared maintenance skills** under `supervisor/skills/`
   - reusable methods that keep maintenance agents coherent
   - agent-agnostic instructions for analysis and compression work

Maintenance agents are not a new governance layer. They are specialized,
asynchronous subordinate roles operating under the workspace supervisor.

## Consequences

### Positive

- The target operating shape becomes explicit early.
- Future activation can happen by inflating declared roles rather than
  inventing new ones under stress.
- The system can separate responsibility from method: agents own loops; skills
  standardize how those loops work.

### Costs

- There is now more structure than active behavior.
- Some declared roles will remain dormant until runtime conditions justify
  activation.

## Alternatives considered

1. **Keep all maintenance work inside the supervisor until pain forces a split.**
   Rejected: this is exactly the path that produces a difficult, archive-bound
   reorg later.

2. **Implement only the two immediately useful maintenance roles.**
   Rejected: local optimization would overweight current pain and under-design
   the durable shape.

3. **Model maintenance work as skills only.**
   Rejected: skills encode method, not ownership, cadence, or escalation
   boundaries.
