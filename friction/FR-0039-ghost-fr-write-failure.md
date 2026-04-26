---
id: FR-0039
title: Tick sessions claim to write FR files that never land on main
status: Open
created: 2026-04-25T20:48Z
detected-by: supervisor-tick-2026-04-25T20-48-43Z
---

# FR-0039 — Ghost FR write failure

## Observation

Multiple tick sessions (18:53Z, 20:48Z, 22:49Z, 02:48Z) emitted events claiming to have written FR-0038 through FR-0043. `ls friction/` consistently shows FR-0037 as the highest. The files were written to tick branches that were never merged to main. The events fire even when the file write is effectively dead-lettered.

This is the third recurrence of FR-0029 (the original ghost-FR pattern): event emission and file write are not atomic, and tick branches strand changes from main.

## Impact

Governance telemetry is systematically dishonest. A session reading events.jsonl would believe FR-0038-0043 existed; a session reading the filesystem finds FR-0037. The meta-loop can't trust its own audit trail.

## Root cause hypothesis

Tick sessions run on named branches (`ticks/YYYY-MM-DD-HH`). They write FR files, commit them, and push — but push goes to the tick branch, not main. Unless attended session merges the branch, the FRs are permanently stranded. Event emission happens in-session before the push, so events precede the branch push regardless of merge state.

## Proposed fix class

- Ticks should not emit `friction_captured` events until after the branch push.
- Alternatively: ticks should write FRs directly to main (requires restructuring the tick's git workflow — significant change).
- Minimum: the tick report should include a checksum of files written vs files present on main before exiting.
