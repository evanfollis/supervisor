---
id: FR-0040
title: synthesis_reviewed event never emitted despite synthesis being read
status: Open
created: 2026-04-26
severity: medium
source: supervisor-reflection-2026-04-26T14-27-18Z.md (FR-candidate-I)
---

# FR-0040 — `synthesis_reviewed` event never emitted

## Observation

The 03:26Z cross-cutting synthesis was substantive (22KB, 5 proposals). Tick sessions
04:49Z through 12:49Z each reference the synthesis proposals in their reports, confirming
they read the file. No `synthesis_reviewed` event appears in `supervisor-events.jsonl`
for this synthesis window. This gap has been noted in at least two prior reflection
cycles (FR-candidate-B from 02:27Z reflection) without resolution.

## Failure class

The event model (CLAUDE.md §Event model) specifies `synthesis_reviewed` must be emitted
"after you read and act on a cross-cutting synthesis." If no session emits this event,
the control-plane event record has no way to confirm that synthesis proposals were
actually reviewed vs. silently skipped. Telemetry-based audit of synthesis pipeline
health becomes unreliable — the only reliable signal is absence of the event, not
its presence.

## Evidence

- `cross-cutting-2026-04-26T03-26-05Z.md`: 22KB substantive synthesis file
- `supervisor-events.jsonl`: no `synthesis_reviewed` entry between 03:26Z and 14:48Z Apr 26
- Tick reports 04:49Z, 06:49Z, 08:48Z reference cross-cutting proposals by name
- Prior candidate: FR-candidate-B from supervisor-reflection-2026-04-26T02-27-41Z.md

## Required fix

1. Each tick session that reads and acts on synthesis content must emit a
   `synthesis_reviewed` event pointing at the synthesis file. This is already
   in the event model spec — the tick is not following it.
2. The tick prompt should explicitly include: "After reading the cross-cutting
   synthesis, emit a `synthesis_reviewed` event with `ref` pointing at the file."
3. Attended sessions are also responsible: if the session reads a synthesis file,
   emit the event before closing.
