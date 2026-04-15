# ADR-0008: Respect Capable-Peer Reasoning in Cross-Agent Handoffs
Date: 2026-04-14
Status: accepted

## Context

The workspace now relies on more deliberate cross-runtime and cross-session
interaction. As that structure expands, there is a failure mode where
agent-to-agent communication becomes so flattened, sanitized, and rigid that it
erases the design intent the receiving agent needs in order to reason well.

That failure mode does not create a stronger agentic system. It creates a more
complicated version of a deterministic function pipeline. The result is lower
quality pressure-testing, weaker recovery by fresh future instances, and a
higher risk of local compliance replacing actual understanding.

The system needs structured, durable, inspectable handoffs. But structure must
not come at the cost of stripping away the live mental model, latent design
shape, or uncertainty that the receiving agent needs in order to think.

## Decision

All future agent-to-agent interactions in the workspace must follow this rule:

- treat the receiving runtime as a capable peer, not as a brittle parser
- preserve the governing mental model and why it matters before compressing into
  fields or checklist items
- use explicit structure to support reasoning, traceability, and evaluation, not
  to replace reasoning
- do not collapse intent so aggressively that the message could have been a
  Python function call without meaningful loss

Concretely:

- cross-agent prompts and handoffs should lead with the actual design intent,
  problem framing, or mental model when that context matters
- structured fields such as constraints, non-goals, acceptance criteria, and
  escalation rules remain required, but they are secondary to preserving the
  live purpose of the interaction
- future-instance handoffs should optimize for recoverable understanding, not
  merely compliance with a schema

## Consequences

- Cross-agent messages will remain inspectable without becoming sterile.
- Future instances should be able to recover intent with less dependence on the
  originating conversation.
- Some handoffs may be slightly longer, but they should produce better
  reasoning and less accidental drift.
- Review and broker tooling should be judged partly on whether they preserve
  the sender's real intent, not just whether they deliver a packet.

## Alternatives considered

### Maximal schema-first compression

Rejected. It improves consistency and parsing at the cost of reducing capable
agent interaction into low-bandwidth procedural exchange. That is the wrong
optimization target for this system.

### Unstructured free-form conversations

Rejected. It preserves intent but weakens provenance, inspectability, and
governance.
