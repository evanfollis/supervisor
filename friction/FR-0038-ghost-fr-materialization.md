# FR-0038: Ghost FR materialization — FRs claimed in events but never written to disk

Captured: 2026-04-28T04:50Z (first detection); confirmed missing 2026-04-28T08:50Z
Source: supervisor-tick observation
Status: open

## What happened

Ticks on 2026-04-28T02:49Z and 2026-04-28T04:50Z both emitted `fr_captured` events referencing
`friction/FR-0038-ghost-fr-materialization.md` and `friction/FR-0039-synthesis-stub-propagation.md`.
Neither file was ever written to disk. The events were false positives — the tick session believed
it wrote the files but the filesystem write silently failed or was not executed.

This is a recurrence of the same pattern: a tick claims a governance artifact was created,
the claim enters `supervisor-events.jsonl`, but subsequent ticks find the artifact absent.

## Why it matters

- Events become unreliable as truth sources when they claim writes that didn't happen
- Future ticks skip FR creation ("already captured") based on a false record
- The friction queue under-reports the real problem count

## Root cause hypothesis

The tick session either:
(a) planned to write the file but was interrupted before executing the Write tool call, or
(b) ran in a sandbox environment where the friction/ path appeared writable but writes were dropped

## Mitigation

A post-write verification step (`ls friction/FR-NNNN-*.md` to confirm the file exists before
emitting the `fr_captured` event) would catch silent write failures. This is a scripts/lib/
concern if automated; for tick sessions, it's a behavioral discipline.

## Status tracking

- 2026-04-28T08:50Z: FR materialized on disk by this tick (was ghost since 2026-04-28T02:49Z)
