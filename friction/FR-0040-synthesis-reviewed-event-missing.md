---
id: FR-0040
title: synthesis_reviewed event not emitted by tick sessions
severity: Medium
created: 2026-04-27
status: Open
source: supervisor-tick-2026-04-27T06-48-08Z (written on main; prior instance on ticks/2026-04-26-20)
---

# FR-0040 — synthesis_reviewed event not emitted by tick sessions

## Observation

The tick prompt requires emitting a `synthesis_reviewed` event after reading a
synthesis file. Tick sessions read synthesis content but historically did not
emit the event. This degraded traceability in the synthesis → dispatch → action chain.

## Evidence

- events.jsonl prior to 2026-04-27T02:49Z: multiple tick sessions read synthesis
  content with no `synthesis_reviewed` event in the same session.
- The tick at 02:49Z and 04:48Z correctly emitted `synthesis_reviewed` — so the
  behavior improved but is not consistently enforced.

## Status

Partially improved: the 02:49Z and 04:48Z ticks emitted the event. The risk
is regression when tick sessions skip synthesis reading under time pressure.

## Fix path

Add `synthesis_reviewed` event emission as an explicit required step in the
tick prompt and wrapper, with a check that it fired before the session exits.
Tier-C (tick prompt and/or wrapper change).
