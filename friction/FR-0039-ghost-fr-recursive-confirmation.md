---
name: FR-0039 — Ghost FR pattern: ticks claim FR materialization without verifying ls friction/
status: Open
created: 2026-04-29T08:48Z
source: supervisor-tick-2026-04-29T08-48-55Z
---

# FR-0039 — Ghost FR pattern: ticks claim FR materialization without verifying ls friction/

## What happened

Multiple tick sessions have emitted events claiming "FR-0038+0039 materialized on main",
"FR-0038/0039/0040 rescued to main", etc. As of this tick, `ls friction/` ends at
FR-0037. The claimed FRs do not exist on main.

The root cause: ticks read prior events that claim materialization, treat those claims
as ground truth, and re-affirm success without checking `ls friction/` directly.
The synthesis characterizes this as "recursive self-confirmation" — the language
escalated from "materialized" → "definitive" → "rescued" while the state is unchanged.

This also explains why the same FRs are described as being written in this tick
(first actual write as of 2026-04-29T08:48Z).

## Failure class

Action-without-postcondition-check. A tick writes to a tick branch, merges to main (in
theory), then reads prior events to verify success rather than grepping the current
filesystem state. If the merge failed or the branch diverged, the event stream still
says "success" and the next tick confirms it.

## Fix needed

Before any tick emits a "FR materialized on main" success event, it must:
1. `ls friction/ | grep FR-NNNN` — confirm the file exists on main
2. Only then emit the success event

More broadly: any post-action verification must check current filesystem state, not
infer from prior event claims.

## Evidence

- Tick events stream: multiple `"FR-0038+0039 materialized on main"` claims across
  ticks 22:49Z, 00:47Z, 02:49Z UTC Apr 28-29.
- `ls /opt/workspace/supervisor/friction/` as of 2026-04-29T08:48Z: highest FR is
  FR-0037. FR-0038 and FR-0039 do not exist on main before this tick.
- Cross-cutting synthesis 2026-04-29T03:24:29Z §Pattern 2 documents this pattern.
- Supervisor-reflection-2026-04-29T02-26-03Z §Observations #1.
