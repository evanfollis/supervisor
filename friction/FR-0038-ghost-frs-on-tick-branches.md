---
id: FR-0038
title: Ghost FRs on tick branches — friction files never reach main
severity: CRITICAL
status: open
created: 2026-04-27
---

# FR-0038: Ghost FRs on tick branches

## Pattern

Tick sessions create FR files (and update active-issues.md) on tick branches that
are never merged to main. Those files exist only on the tick branch where they were
created. Subsequent ticks that run on a fresh tick branch (or on main) find no
evidence these FRs ever existed.

Events log claims like "FR-0038 written on main" have been emitted multiple times.
On main, the friction/ directory ends at FR-0037. The divergence is invisible to
any session reading from main.

## Root cause

Tick sessions run under a branch-per-tick model. Tier-A writes (friction, events,
active-issues) are committed to the tick branch, not to main. The autocommit job
writes Tier-A paths on main, but only picks up changes that exist in the working
tree at commit time — it does not merge tick branches. Since tick sessions exit
before autocommit runs, their Tier-A writes land on dead branches.

## Consequences

- FR numbering on main is frozen; new FRs assigned on tick branches collide
- active-issues.md on main is perpetually stale
- Events log claims actions that did not happen on main
- Synthesis and reflections that read from main see a degraded truth surface

## Fix direction

Tick sessions should write Tier-A artifacts directly to main (or autocommit should
merge tick-branch Tier-A paths to main on every commit). The existing architecture
creates a false separation: tick branches carry "governance artifacts" but the
governance surfaces they're supposed to update remain on main.

Attended session must decide: (a) tick sessions always run on main, (b) autocommit
merges Tier-A paths from tick branches, or (c) an explicit merge step runs after
each tick. This is an ADR-class decision.
