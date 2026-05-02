---
id: FR-0041
title: Synthesis-to-execution gap — 0 of 40+ proposals landed in 11 cycles
status: Open
filed: 2026-05-02
source: supervisor-tick-2026-05-02T06-48-26Z
projects: supervisor, all
---

# FR-0041 — Synthesis-to-execution gap

## What happened

11 cross-cutting synthesis cycles have run. 40+ proposals sit in
`supervisor/handoffs/INBOX/`. Zero proposals have been implemented in any
project. INBOX has grown from ~15 to 40 items. The dispatch obligation
(24h to route or defer) has been violated for nearly every synthesis.

## Why proposals don't land

Proposals target Tier-B/C surfaces (scripts/lib/, charter files, existing ADRs,
CLAUDE.md) that tick sessions cannot write. The only path to implementation is
an attended executive session — which has not occurred.

No decision exists on whether tick sessions should have autonomous authority
for safe Tier-B proposals. The question has been open since at least synthesis
cycle 8.

## Concrete consequence

The reflection/synthesis loop is generating high-fidelity diagnosis with zero
execution throughput. This is the worst-of-both-worlds outcome: the diagnostic
cost is paid but the improvement is not captured. The loop is a growing liability.

## What would fix it

One of:
1. **Attended principal triage**: bulk disposition of INBOX (execute, defer, or
   close each item); even bulk "won't-fix" would restore URGENT signal quality
2. **Autonomous tick authority for Tier-B proposals**: explicit ADR expanding
   what tick sessions may implement without attended approval
3. **Scope reduction**: reduce synthesis proposal surface to only items that
   ticks can implement or that require principal decisions (not Tier-C scaffolding)
