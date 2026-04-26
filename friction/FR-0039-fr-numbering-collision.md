---
name: FR-0039 — FR numbering collision in unattended ticks
description: Multiple consecutive ticks each claim to write FR-NNNN files but none are written; event stream shows sequential claims for the same number range
status: Open
created: 2026-04-25T20:48Z
discovered-by: supervisor-tick-2026-04-25T20-48-43Z
---

# FR-0039 — FR numbering collision in unattended ticks

## Status: Open

## Observed behavior

Three consecutive ticks (18:47Z, 20:48Z, 22:49Z on 2026-04-25) each emitted events claiming new FR files were written:
- 18:47Z tick: "FR-0038 (synthesis empty stubs)"
- 20:48Z tick: "FR-0039 (fr-numbering-collision)"
- 22:49Z tick: "FR-0040 (atlas gate/cache misalignment)"

None of these files exist in `friction/`. The highest actual FR on disk is FR-0037 (written 2026-04-25T13:20Z).

## Root cause

The tick's FR-creation step and the event-emission step are not atomic. Events fire even when the file write was not attempted or failed silently. The tick determines the next FR number by scanning `friction/` at session start, but if the write never lands, subsequent ticks see the same highest number and attempt to claim the same slot, or the tick's write attempt silently fails without surfacing an error.

This is a recurrence of the same pattern documented in FR-0029 (ghost FRs from prior tick cycles). FR-0029's resolution ("write the files more carefully") was not structural.

## Fix required

The tick's FR write step must verify the file exists after writing. If the write fails, emit a `fr_write_failed` event naming the file, rather than claiming success. This is a `reflect.sh` / `supervisor-tick.sh` Tier C change.

Alternatively, the tick should not emit `session_reflected` events claiming FR records until the file stat confirms the file exists and is >100 bytes.

Tier C work — requires attended session.
