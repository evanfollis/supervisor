---
name: FR-0039 — FR numbering collision in unattended ticks
description: Multiple consecutive ticks each claim to write FR-NNNN files but none are written; event stream shows sequential claims for the same number range
status: Partially resolved (FR-0038–0043 written to main by tick 2026-04-26T04:49Z; structural fix pending)
created: 2026-04-25T20:48Z
discovered-by: supervisor-tick-2026-04-25T20-48-43Z
---

# FR-0039 — FR numbering collision in unattended ticks

## Status: Partially resolved

## Observed behavior

Three consecutive ticks (18:47Z, 20:48Z, 22:49Z on 2026-04-25) each emitted events claiming new FR files were written:
- 18:47Z tick: "FR-0038 (synthesis empty stubs)"
- 20:48Z tick: "FR-0039 (fr-numbering-collision)"
- 22:49Z tick: "FR-0040 (atlas gate/cache misalignment)"

None of these files existed in `friction/` on main. The 02:48Z tick (2026-04-26) wrote FR-0038–0043 on its tick branch; the 04:49Z tick materialized them on main.

## Secondary collision

The aged tick branch `ticks/2026-04-20-22` also claimed FR-0038 for a DIFFERENT finding (`FR-0038-current-state-uncommitted-after-reflection.md`). That branch's FR-0035, FR-0036, FR-0037 also conflict with main's current FR-0035, FR-0036, FR-0037 (different file names/content). This branch cannot be cleanly merged without manual FR renaming.

## Root cause

The tick's FR-creation step and event-emission step are not atomic. Events fire even when the file write was not attempted or failed silently. See also FR-0029 (prior recurrence) and FR-0041 (structural integrity diagnosis).

## Fix required

See INBOX: `proposal-atomize-fr-creation-2026-04-26T03-37-07Z.md`. Tier C — attended session.
