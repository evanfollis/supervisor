# ADR-0006: Active idea-focus queue derived from the ledger

Date: 2026-04-14
Status: accepted

## Context

The novel idea ledger solves durable capture, but by itself it risks becoming a
growing archive rather than an operating surface.

The user requirement is explicit: the system must be good at absorbing noise
while identifying compoundable value through ongoing interaction. That means
the supervisor should not reread the entire idea archive on every reentry.

It needs a compressed, actively maintained working set.

## Decision

Add a derived **idea-focus queue** generated from `supervisor/ideas/` into
`runtime/.meta/` and refreshed automatically by systemd.

The focus queue:

- includes only active or recently changed ideas
- prioritizes ideas by urgency, leverage, and staleness
- exposes a small top-of-queue surface for the supervisor to read on reentry
- preserves the full ledger as the durable archive beneath it

The focus queue is derivative, not canonical. The underlying idea records
remain the source of truth.

## Consequences

### Positive

- The supervisor reads a queue, not an archive.
- Deferred and sandboxed ideas stay governable without becoming invisible.
- Novelty can be compressed into a small active surface while long-tail noise
  remains stored but not foregrounded.

### Costs

- Another derived runtime artifact to keep healthy.
- Priority heuristics will initially be crude and should be refined over time.

## Alternatives considered

1. **Read all idea records on every reentry.**
   Rejected: scales poorly and encourages the archive to become clutter.

2. **Make the idea ledger itself ordered and mutable by hand.**
   Rejected: too manual and easy to drift.

3. **Use an LLM synthesis pass only.**
   Rejected: useful later, but deterministic queue generation is the correct
   first layer.
