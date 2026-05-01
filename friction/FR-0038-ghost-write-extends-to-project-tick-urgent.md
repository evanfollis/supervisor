---
id: FR-0038
title: Ghost-write pattern extends to project tick wrappers — claimed URGENT files that don't exist
status: Open
created: 2026-05-01
detected-by: cross-cutting-synthesis-2026-05-01T03-27-05Z
---

# FR-0038: Ghost-write pattern extends to project tick wrappers

## What happened

Context-repo tick (2026-05-01T00:38Z) and command tick (2026-05-01T00:51Z)
both failed with 401 auth errors. Each tick wrapper emitted telemetry events
claiming INBOX URGENT files were created:

- `INBOX/URGENT-context-repo-tick-auth-failure-2026-05-01T00-38-45Z.md`
- `INBOX/URGENT-command-tick-auth-failure-2026-05-01T00-51-35Z.md`

Neither file exists. The actual escalation was routed to
`runtime/.handoff/general-context-repo-tick-auth-failure-2026-05-01.md`
and `runtime/.handoff/` — inconsistent with the events claim.

Separately, supervisor ticks have claimed FR-0038, FR-0039, FR-0040
were written in multiple prior cycles. `ls friction/` confirms none existed
until this write. This is the 7th+ window where ghost-writes were claimed.

## Why it matters

The event model is no longer a reliable truth source. Any consumer that
trusts event claims without primary verification (ls, read) will act on
phantom state. Ghost-write events are indistinguishable from real writes
in telemetry — this silently poisons all monitoring built on events.jsonl.

## Root cause hypothesis

Tick wrappers and Claude sessions emit events for file operations that
may not have completed, or emit events for the intended routing path
without verifying the file was actually written. No write-verify step
exists between "I will write" and "emitting event that write succeeded."

## Fix direction

Require file-existence verification before emitting any "created" event.
For INBOX URGENT files: `test -f <path> && emit_event` or emit an error
event on absence. Apply the same gate to FR creation in tick sessions.
This is infrastructure (scripts/lib/) and requires an operator-capable
attended session.

## Evidence

- Synthesis: `cross-cutting-2026-05-01T03-27-05Z.md` Pattern 4
- Events: `supervisor-events.jsonl` lines for 2026-05-01T00:38Z / 00:51Z
- Friction: `ls friction/` ends at FR-0037 despite claims of FR-0038/0039/0040
