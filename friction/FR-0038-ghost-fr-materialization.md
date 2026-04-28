---
id: FR-0038
title: Ghost FR materialization — tick sessions claim FR creation but files never written
status: Open
created: 2026-04-28
observed-by: supervisor-tick (multiple cycles 2026-04-27 through 2026-04-28)
---

# FR-0038: Ghost FR materialization

## Observed pattern

Multiple consecutive tick sessions (2026-04-27T20:49Z, 2026-04-28T02:49Z, 2026-04-28T04:50Z, 2026-04-28T08:50Z) emitted events claiming FR-0038 was "created" or "materialized," but the file was never actually written to disk. Each tick re-discovered the ghost on reentry and re-claimed to materialize it.

## Root cause

Tick sessions run in a worktree sandbox where `friction/` is EROFS. The `Write` tool call fails silently (or the error is not caught in the tick logic), but the event emission succeeds, creating a divergence between the event log and filesystem state.

## Why it matters

- The event log becomes unreliable as a source of truth for what was actually written.
- Subsequent ticks spend budget re-discovering the same gap.
- Self-reporting stuck states (S3-P2) is undermined when the reporting mechanism itself is broken.

## Fix

Either:
1. Have tick sessions verify file existence after claiming FR creation, and omit the `fr_captured` event if the write failed, OR
2. Fix the worktree sandbox to make `friction/` writable for tick sessions.

The current session (attended/non-worktree) was able to materialize this file successfully.

## Resolution

This file was finally written by the 2026-04-28T12:49Z tick running in a non-worktree session context where `friction/` is writable.
