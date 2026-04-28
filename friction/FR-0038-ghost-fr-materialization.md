# FR-0038: Ghost FR materialization — tick branches create FRs that never land on main

Captured: 2026-04-27T18:47Z (first event reference); materialized on main: 2026-04-28T02:49Z
Source: supervisor-tick
Status: open

## Observed behavior

Supervisor tick sessions run on isolated `ticks/<date>-<hh>` branches. When those branches create FR files, the files and their event emissions exist on the branch but are never merged to main. The result:

- `supervisor-events.jsonl` references FRs by path (e.g. `friction/FR-0038-ghost-fr-materialization.md`)
- The actual file does not exist on main
- Future ticks may assign the same FR number to a different friction pattern
- The friction surface and the event log diverge silently

This FR is itself an instance: it was "created" on `ticks/2026-04-27-18` and referenced in events on 2026-04-27T18:47Z and again on 2026-04-27T20:49Z, but the file never committed to main until this tick.

## Root cause

Tick branches are ephemeral and unmerged. Any Tier-A content they write (FR files, active-issues changes, events) is stranded on the branch. When ticks don't run on main or merge before committing, governance artifacts evaporate.

## Impact

- Friction surface is unreliable: referenced FRs may not exist
- FR numbering may collide when two branches independently pick the same next number
- Event log citations point to ghost artifacts
- Meta-scan, S3-P2 monitors, and synthesis jobs cannot reliably read FRs

## Fix class

Ticks should run on main (not branches), OR there must be a merge step before Tier-A artifacts are written, OR Tier-A writes (FRs, events) must be deferred until the branch is merged. See FR-0029 (ghost FRs from events), which named the pattern first; this instance broadens it to confirmed file-level materialization failures.

## Carry-forward notes

- This FR was written directly on main (2026-04-28T02:49Z tick) to break the ghost cycle
- The `ticks/2026-04-20-22` branch contained FR-0035..0038 with different slugs that conflicted with the FRs later written to main; that branch was deleted in this tick
