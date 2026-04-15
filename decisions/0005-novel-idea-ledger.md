# ADR-0005: Novel idea ledger as a durable control-plane surface

Date: 2026-04-14
Status: accepted

## Context

The supervisor now has a conceptual model for handling novelty:

- an ideal-state interaction model
- an idea pressure-testing model
- a playbook for novel idea intake and pressure testing

What was still missing was a durable object surface for the ideas themselves.
Without that, novel proposals remain conversational and easy to lose, repeat,
or prematurely implement.

The user requirement is to give new ideas a path into the system that:

- assigns a durable identity
- records current disposition
- captures evidence and follow-up
- supports pushback without falling into refusal or drift

## Decision

Add `supervisor/ideas/` as a first-class durable control-plane surface with a
small CLI ledger for creating, updating, listing, and showing idea records.

Each idea record has:

- a stable ID (`IDEA-NNNN`)
- a slug and title
- a lifecycle status
- a concise summary
- scope and target-layer classification
- evidence, artifact refs, and disturbance notes
- a next-step field
- a history log of state changes

The supervisor owns this ledger. Novel ideas should be captured here before
they are allowed to change workspace structure.

## Consequences

### Positive

- Novel proposals become addressable control-plane objects rather than chat
  fragments.
- The supervisor can revisit deferred or rejected ideas without reconstructing
  them from scratch.
- Pressure testing becomes easier to execute consistently because the evidence
  and disposition live in one place.
- Future automation can operate over a stable queue of idea records.

### Costs

- Another durable surface to maintain and prune.
- Risk of becoming bureaucratic if ideas are logged without actual
  pressure-testing or decisions.

## Alternatives considered

1. **Keep ideas inside ADRs only.**
   Rejected: too heavy for early-stage proposals and too late for deferred or
   rejected ideas that still need durable memory.

2. **Use runtime JSONL only.**
   Rejected: runtime state is not the right durability class for long-lived
   strategic proposals.

3. **Rely on transcripts and handoffs.**
   Rejected: too lossy and too expensive to search as the main novelty queue.
