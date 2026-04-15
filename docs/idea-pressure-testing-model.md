# Idea Pressure-Testing Model

This document defines how novel ideas, experiments, and structural changes
should enter the system without steamrolling it.

## Problem

Novel ideas are valuable, but they are structurally dangerous when they bypass
the governance stack and move straight to implementation.

The system needs a way to investigate and integrate strong ideas while
resisting ideas that add noise, complexity, or ungoverned surface area.

## Rule

A novel idea should be treated as a governance input before it is treated as an
implementation request.

That means the first question is not "can we build this?" It is:

"What kind of change is this, what would it disturb, and what evidence would
justify adoption?"

## Default lifecycle

Every novel idea should move through these states:

1. `captured`
2. `framed`
3. `pressure_tested`
4. one of:
   - `adopted`
   - `sandboxed`
   - `deferred`
   - `rejected`

## State meanings

### Captured

The idea has been recorded in durable form in `supervisor/ideas/` with a clear
statement of the proposed change.

### Framed

The supervisor has identified:

- what layer the idea targets
- whether it is project-local or cross-project
- what current policy or structure it would alter
- what evidence would count in its favor or against it

### Pressure-tested

The system has examined:

- expected upside
- complexity cost
- governance impact
- blast radius
- reversibility
- what would happen if the idea partially succeeded but expanded the surface
  area anyway

### Adopted

The idea has enough evidence and fit to become policy, playbook, or scoped
implementation.

### Sandboxed

The idea is promising but not mature enough for broad integration. It may be
tried in a bounded scope with explicit success and stop conditions.

### Deferred

The idea may be useful later, but current timing, evidence, or dependency state
is insufficient.

### Rejected

The idea does not currently justify its cost, risk, or structural disturbance.

## Pushback standard

Pushback should be intelligent, not performative.

The system should not reflexively refuse. It should instead:

- narrow the idea to its strongest falsifiable core
- identify what existing structure it would disturb
- recommend the smallest valid test surface
- explain why immediate broad adoption would be premature, if so

## Admission questions

Before an idea is allowed to reshape the stack, answer:

1. What problem does this solve that current policy or structure does not?
2. Which layer should own this if it works?
3. What recurring judgment would this eliminate or compress?
4. What new operational burden would it create?
5. Can it be tested without broadening authority or surface area first?
6. What evidence would cause us to reject it quickly?

## Structural guardrail

No idea should move directly from `captured` to broad implementation when it
changes:

- governance boundaries
- authority allocation
- cross-project substrate
- telemetry or truth contracts
- persistent workflow expectations

Those changes require pressure testing first.

## Working-set rule

The supervisor should not reread the entire idea archive on every session.
Active novelty should be compressed into the derived idea-focus queue under
`runtime/.meta/`, and only the ideas surfaced there should demand routine
attention.
