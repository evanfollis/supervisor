---
name: FR-0038 ghost-write event claims
description: Tick sessions emit events claiming to have written files (FRs, active-issues updates) that are not present on the main branch — either the write failed silently or the tick operated on a branch that was never merged.
status: open
created: 2026-05-01
sources:
  - tick-2026-05-01T08-49-09Z (first verified write of FR-0038/0039 on a branch)
  - tick-2026-05-01T16-48-26Z (event said FR-0038/0039/0040 written; none appeared on main)
related:
  - FR-0022-executive-event-claimed-file-not-written.md
  - FR-0029-ghost-fr-claimed-in-events.md
---

# FR-0038 — Ghost-write event claims: tick artifacts on unreachable branches

## What happened

Multiple supervisor ticks emitted events claiming to have written friction records
(FR-0038, FR-0039) and updated active-issues. A subsequent check of main found none of
those files present. The writes landed only on tick branches that are accumulating without
being merged back to main.

## Pattern

- Tick branch `ticks/2026-05-01-08` (d548ac8): FR-0038/0039 written to `friction/` on branch
- Tick branch `ticks/2026-05-01-16` (27f264d): event claimed FR-0038/0039/0040 written; commit
  contains only `system/verified-state.md` and a session-summary archive
- Main branch: highest FR is 0037 as of 2026-05-01T18:47Z — 5 claimed-but-missing files

## Root cause

Tick branches are created by the wrapper script for each session, but no auto-merge or
rebase into main follows. Governance artifacts written during tick sessions are siloed per
branch. Unless an attended session merges or cherry-picks the tick branches, the artifacts
are effectively dead.

## Why this matters

Friction records, active-issues updates, and URGENT handoffs written in tick branches are
invisible from main. The next tick or attended session starts from a state that does not
include those artifacts, causing the same issues to be rediscovered and re-reported cycle
after cycle (see FR-0039 rewritten across multiple ticks).

## Resolution path

Short-term: write all durable governance artifacts in the current interactive tick directly
on main (this file is one). Long-term: ADR or playbook proposal for merging tick branches
into main, or restructure so ticks never create separate branches for Tier-A writes.

## Status

Open — structural problem persists. This write is the first landing of FR-0038 on main.
