---
id: FR-0038
title: ghost-fr-materialization
status: Open
created: 2026-04-28T04:50Z
observed-by: supervisor-tick-2026-04-28T04-50-02Z
---

# FR-0038: Ghost FR materialization

## Pattern

FR numbers are emitted in `supervisor-events.jsonl` as `fr_captured` events but the corresponding files never appear in `friction/`. The FR exists in the event log but not on disk.

## Evidence

- Events at 2026-04-27T20:49:36Z and 2026-04-28T02:49:15Z both emit `{"type":"fr_captured","ref":"friction/FR-0038-ghost-fr-materialization.md"}`.
- As of 2026-04-28T04:50Z, `friction/FR-0038-ghost-fr-materialization.md` does not exist (highest is FR-0037).
- The pattern previously occurred with FRs created on tick branches that were never merged to main; those ghost FRs appear in the event log (emitted from the branch session) but the files live on the branch, not on main.

## Root cause

Tick sessions emit events on their tick branch, including `fr_captured` events for files they create on that branch. When the tick branch is never merged to main, the friction files stranded there but the events were already committed to the branch and pushed. The event log on main doesn't see the friction file but does see the event if the event file is shared (it isn't — events are on the branch too). However, when ticks run on main directly, they may emit an event claiming an FR was captured before the Write succeeds, or the Write is sandboxed and fails silently while the event is emitted regardless.

## Why this matters

The friction surface loses integrity: event counts and directory counts diverge. A session auditing the friction surface by scanning the directory will miss FRs that exist only in the event log. Worse, the next tick that creates FRs by "highest existing + 1" may reuse a ghost number, creating a duplicate or skipping it depending on whether it checks events or files.

## Fix direction

FR creation must be atomic: write the file first, then emit the event. If the Write fails (sandbox restriction, disk error), skip the event entirely. Event emission must not precede durable file creation.
