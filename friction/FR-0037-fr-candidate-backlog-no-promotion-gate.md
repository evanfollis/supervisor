---
id: FR-0037
title: FR candidates named in reflections never promote to FR files without attended action
status: open
filed: 2026-04-20
---

# FR-0037 — FR candidate backlog, no promotion gate

## What happened

The reflection pass correctly identifies friction signals and names them as
"FR-NNNN-candidate" in its output. But there is no mechanism that converts these
candidates to actual FR files. The candidates sit in reflection markdown until an
attended session (or this tick) reads them and promotes them. In practice this has
meant multiple candidates (FR-0035 through FR-0038) accruing across 2-3 reflection
cycles before being filed.

## Structural gap

The meta-loop → attended session → actuation path is the intended pattern, but for
low-friction items like filing an FR record, the cycle time (one reflection window =
12h, two = 24h) adds unnecessary latency. The reflection pass runs with
`--disallowedTools` and cannot write FR files directly. The tick CAN write FR files
(Tier A), so candidates surfaced in reflections should be promoted within one tick
cycle, not deferred to the next attended session.

## Proposed fix

Tick prompt should include a step: "read the most recent supervisor reflection and
promote any named FR-NNNN-candidate entries to actual FR files." This is already
within tick authority (friction/ is Tier A).

## Status: Open
