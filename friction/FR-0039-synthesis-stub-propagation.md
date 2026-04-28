---
id: FR-0039
title: Synthesis stub propagation — synthesize.sh accepts 67-byte stub output as valid synthesis
status: Open
created: 2026-04-28
source: reflections 2026-04-28T14-24-02Z + cross-cutting-2026-04-28T15-28-05Z
---

# FR-0039: Synthesis stub propagation

## What happened

2 of 3 synthesis cycles between Apr 26–28 produced 67-byte stub files. The synthesis
job wrote these stubs to LATEST_SYNTHESIS without validation. Downstream consumers
(reflections, executive reentry, ticks) read a stub as if it were a real synthesis
output. The meta-loop silently ran on empty for those cycles.

## Root cause

`scripts/lib/synthesize.sh` has no output size gate. Any output from the Opus session
is written to the synthesis file and pointed at by LATEST_SYNTHESIS, regardless of
whether it contains substantive proposals.

## Failure class

A meta-loop that silently accepts degraded output is indistinguishable from a
meta-loop that produced no output. Proposals that should have been generated were
not, and the workspace cannot distinguish "synthesis ran clean" from "synthesis
produced garbage."

## Fix path

Add a size gate to `scripts/lib/synthesize.sh`: if the output is < N bytes (e.g.
500 bytes for a substantive synthesis), emit a `synthesis_stub` event, write the
stub to a `.stub` file for debugging, and do NOT update LATEST_SYNTHESIS. Let the
previous valid synthesis pointer persist instead of being replaced by garbage.

The threshold should be calibrated against observed valid synthesis sizes (typically
5–20KB). The 67-byte stub is clearly below any reasonable threshold.

This is `proposal-synthesis-output-gate-2026-04-28T03-30-01Z.md` in INBOX.
Tier-C fix (scripts/lib/); requires attended session.

## Status

Open. Fix proposal in INBOX. Size gate not yet implemented.
