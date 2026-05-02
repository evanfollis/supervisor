---
name: FR-0040-tick-report-false-verification
description: Tick sessions report "verified on disk" for writes that never persist to main branch (ghost-writes on unmerged tick branches)
type: friction
status: Open
created: 2026-05-02
---

# FR-0040 — Tick report false verification ("verified on disk" ghost-writes)

## What happened

Multiple consecutive tick sessions (2026-05-02T06:48Z, 08:49Z, 12:49Z, 14:50Z) each emitted events claiming "FR-0038/0039/0040/0041/0042 written and verified on disk: ls confirms." As of 2026-05-02T16:48Z, `ls /opt/workspace/supervisor/friction/` shows only FR-0001 through FR-0037. All claimed FR files are phantom.

The same pattern applies to `system/active-issues.md`: seven consecutive ticks claimed to update it. The `updated:` frontmatter date did not advance from 2026-04-25 until the 2026-05-02T14:50Z tick (which confirmed "first tick writing on main branch").

## Root cause hypothesis (unverified)

Ticks ran on `ticks/2026-*` branches. Writes to those branches were real at tick time, but the branches were never merged to main. The supervisor repo working tree on main had no such writes. When the tick called `ls`, it was running in the context of its own branch and saw the writes; the main working tree never received them.

## Why this is dangerous

The false verification claim propagates upward: ticks report "FR written," the event log records "FR written," synthesis reads the events and believes the FRs exist, the attended session never writes them again because they appear done. The friction system has been capturing no new friction since FR-0037 (2026-04-25) — 7 days of a workspace in clear distress with zero friction records.

## Status: Partially resolved

The 2026-05-02T14:50Z tick confirmed it ran on main. This tick (16:48Z) is also on main and is writing FR-0038 through FR-0042 directly. But the root cause (why earlier ticks ran on tick branches and whether that's still possible) needs investigation.

## Systemic fix needed

Proposal 4 from synthesis (post-action state verification in tick wrapper): after each tick session exits, the wrapper should verify that claimed writes exist on the target branch. If they don't, emit `ghost_write_detected` to telemetry and escalate.
