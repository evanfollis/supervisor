---
name: FR-0040 — synthesis_reviewed event not emitted by tick sessions
status: Open
severity: Medium
created: 2026-04-26
source: supervisor-reflection-2026-04-26T14-27-18Z + synthesis-2026-04-26T15-25-01Z
---

# FR-0040: synthesis_reviewed event not emitted by tick sessions

## Observation

The tick session charter requires emitting a `synthesis_reviewed` event after reading a synthesis file. Tick sessions read synthesis content but do not emit the event. This means the event log has no record of which ticks reviewed which synthesis files.

## Why it matters

The event log is the control plane's source of truth for what work has been done. Missing `synthesis_reviewed` events make it impossible to tell, from the log alone, whether the most recent synthesis was read. This degrades the traceability of the synthesis → dispatch → action chain.

## Fix path

Tick sessions should emit `synthesis_reviewed` with the synthesis file path as `ref` immediately after reading synthesis content. This is a discipline fix, not a structural one. The tick prompt already calls for this; the gap is enforcement.

Alternatively, the synthesis reviewer step could be extracted to a named substep with an explicit event gate (if no synthesis_reviewed event from this tick, log WARN).

## This file

Written on main by an interactive tick session (2026-04-26T20:48Z). Previous instances exist on tick branches only.
