# Maintenance Agent Framework

Maintenance agents are specialized asynchronous roles operating under the
workspace supervisor. They are not a new governance layer. They exist so the
supervisor does not have to balance every parallel optimization concern in one
synchronous loop.

## Design rule

Use agents for responsibility. Use skills for method.

An agent owns:

- scope
- trigger
- cadence
- input surfaces
- output artifacts
- escalation rules

A skill provides:

- reusable analysis method
- repeatable structure
- cross-agent coherence

## Why define the full structure early

If the structure is deferred until pain is acute, the system will grow around
overloaded dual-role loops and later reorganization will be expensive and
partial.

The right move is to define the full target shape now and activate roles over
time as evidence justifies it.

## Maintenance-agent rules

Every maintenance agent must have:

- a manifest under `maintenance-agents/`
- a narrow responsibility boundary
- declared input surfaces
- a single primary output artifact class
- explicit escalation conditions
- one or more shared skills it relies on

Do not activate a maintenance agent unless its queue, outputs, and failure mode
are distinct enough to justify it.

## Initial framework roles

The framework currently defines five roles:

1. `policy-compressor`
2. `ambiguity-watcher`
3. `friction-analyst`
4. `novelty-triager`
5. `trace-auditor`

These are the clean target shape. They may remain `planned` or `inactive`
until activation is warranted.

## Activation rule

A role should only move from `planned` to `active` when:

- its input stream exists
- its output artifact is defined
- the supervisor can state what would be missed if that role did not exist

## Relationship to the supervisor

The supervisor remains the governor. Maintenance agents are subordinate
analytical loops that refine the system in parallel and report upward through
their artifacts and escalation contracts.
