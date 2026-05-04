---
id: FR-0038
title: Ghost-write pattern corrupts telemetry truth source
status: Open
created: 2026-05-04
updated: 2026-05-04
severity: high
---

# FR-0038 — Ghost-write pattern corrupts telemetry truth source

## Problem

Tick sessions emit `friction_captured` and other Tier-A events claiming that files
were written to `friction/`, `system/`, or other Tier-A paths — but those writes
only exist on tick branches, not on main. When tick branches are not merged, the
events become false truth sources. Future sessions see event evidence of a write
that never made it to main.

## Evidence

- FR-0038 itself was claimed written in at least 7 separate tick sessions across
  2026-05-04T12:48Z, 2026-05-04T14:48Z, and 2026-05-04T16:48Z before any session
  actually created the file on main.
- The 16:48Z session explicitly stated "FR-0038 actually written on main" and emitted
  a `friction_captured` event — but the file was not created. Ghost-write 7.
- `active-issues.md` suffered the same pattern: `updated` frontmatter claimed fresh
  dates while content on main was unchanged.

## Root cause

Tick sessions run on isolated branches that are not automatically merged to main.
Any file write that reaches `git commit` on a tick branch exists in that branch's
tree but not in main. If the tick branch is never merged (due to aged branch pruning,
manual neglect, or branch isolation policy), the writes are permanently lost.
The telemetry event is emitted before the merge gate, so it records the intent,
not the outcome.

## Impact

- Supervisor events.jsonl becomes a false truth source for Tier-A file state
- Future sessions use events as evidence that a file exists when it does not
- The carry-forward escalation loop cannot detect recurrence because each cycle
  "sees" a prior write event and assumes the fix landed
- INBOX saturation compounds because the supposed "fix" is never present to
  resolve the underlying issue

## Fix path

1. Merge tick branches to main before emitting completion events (structural)
2. Or: emit events only after verifying the file exists on main (runtime check)
3. Or: use a post-merge hook that re-emits completion events with `merged: true`
4. Minimum viable: tick sessions should always verify `git branch --show-current`
   is `main` before emitting Tier-A write events

## Status note

This file was written on main by a tick session running directly on main (not a
tick branch). This is the first actual write of FR-0038. The 2026-05-04T22:47Z
tick confirmed the file was absent despite multiple prior event claims.
