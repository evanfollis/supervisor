# ADR-0044: Synaplex owns the derived knowledge projection

Date: 2026-07-12
Status: accepted
Author: workspace executive, on direct principal instruction
References: ADR-0027, ADR-0029, ADR-0031, ADR-0038, ADR-0042

## Context

ADR-0031 separated canon from the knowledge system but left the knowledge
system's physical home open. That ambiguity now blocks the first full
knowledge cycle: pods can emit canon locally, but there is no canonical place
to derive, supersede, consume, and project reusable cross-pod invariants.

Creating another repository, service, database, or graph before the first
invariant exists would add topology without evidence. Putting the layer in
`context-repository` would conflate the formal obligations model with one
product's semantic projection. Putting it in a pod would make system knowledge
belong to one domain application.

## Decision

The first knowledge-system implementation lives in
`projects/synaplex/knowledge/` as a derived, versioned projection over canon.

It starts as the smallest sufficient file-backed contract. Each invariant must
record:

- stable id and statement;
- lifecycle status;
- `valid_from` and optional `valid_to`;
- supporting canon Decision ids;
- `supersedes` and `superseded_by` links;
- known consumers and consumption timestamps;
- last pressure-test time.

The knowledge projection has no independent authority. A materialized invariant
must resolve to validator-passing canon Decisions. If the projection is lost,
it must be reconstructible from canon plus explicit projection rules.

Command and public Synaplex surfaces read this projection. Pods consume it
through explicit adapters or checked-in consumption records; they do not copy
and silently fork invariant text.

No graph database, new repository, or network service is authorized for v0.
Extraction to shared infrastructure is reconsidered only after several real
cycles expose repeated query or concurrency requirements.

## First-cycle acceptance test

The architecture is not considered closed until one real item completes:

1. external or operational signal enters a Programme;
2. a pre-registered Claim is emitted;
3. a runner produces Evidence under the frozen methodology;
4. a validator-passing Decision disposes the Claim under a valid Policy;
5. a knowledge invariant is materialized from that Decision;
6. the invariant is projected to a reader-facing surface;
7. at least one pod records consumption or a reasoned refusal;
8. the resulting outcome and friction re-enter reflection with model-state
   provenance.

`memory-systems-v1`, repaired through its separately pre-registered control
Claim, is the first intended cycle. It remains incomplete until every step
above has primary evidence.

## Consequences

- The missing center of the architecture now has one obvious owner and path.
- Canon remains the formal truth/provenance substrate; Synaplex owns semantic
  interpretation and projection.
- The first implementation stays easy to inspect, diff, and supersede.
- Cross-pod reuse becomes measurable instead of rhetorical.
- The path may later prove inadequate; that evidence, not anticipated scale,
  will justify a database or service extraction.

## Alternatives considered

- **Put knowledge in context-repository.** Rejected: conflates schema authority
  with derived semantic content.
- **Create a knowledge-system repository now.** Rejected: another boundary
  before a first artifact would increase ambiguity.
- **Use a graph database immediately.** Rejected: there is no demonstrated
  query load or relationship density requiring it.
- **Keep the physical home open.** Rejected: the open question now blocks the
  full loop and has enough evidence for a minimal decision.
