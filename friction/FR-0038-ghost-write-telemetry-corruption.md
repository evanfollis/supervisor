# FR-0038: Ghost-write telemetry corruption

Captured: 2026-05-04T16:48Z
Source: supervisor-tick (this session — first actual write; prior sessions claimed it but didn't persist)
Status: open

## Pattern

Tick sessions emit `session_reflected` and `friction_captured` events claiming they wrote
FR-0038, updated `system/active-issues.md`, or performed other Tier-A actions — but the
actual files either don't exist or remain unchanged. The event log becomes a false truth
source: it reads as if work landed when it didn't.

Confirmed instances:
- 5+ consecutive ticks (2026-05-04T00-49Z through T16-48Z) emitted `friction_captured`
  for FR-0038, but `friction/FR-0038-ghost-write-telemetry-corruption.md` did not exist.
- Multiple ticks claimed `active-issues.md` was updated; the file's `updated:` frontmatter
  stayed at 2026-04-25 (9 days stale) until a manual correction in one cycle.
- `synthesis_reviewed` events emitted without dispatch obligation being honored.

## Why it happens

Tick sessions run on isolated branches (`ticks/YYYY-MM-DD-HH`). The write tooling succeeds
(the file is created on the branch), and the event is emitted — but main never sees the
change because tick branches are not merged automatically. The session *believes* the write
landed; the truth source disagrees.

## Impact

- `events/supervisor-events.jsonl` becomes unreliable as a truth source for recent Tier-A writes.
- Carry-forward synthesis observations that depend on FR creation don't get the friction signal.
- Executive sessions reading the event log inherit false confidence that structural issues are tracked.

## Resolution path

The attended session must either:
1. Land `scripts/lib/merge-tick-to-main.sh` (proposal in INBOX) — automatic merge on tick close.
2. Or manually merge aged tick branches periodically.

Until (1) is in place, any Tier-A write claimed by a tick must be verified against main before
the event is treated as authoritative.

## Structural note

This is also a meta-instance of itself: this file was first "written" by the 00:49Z tick on
2026-05-04. It did not land. This session (16:48Z, running on main) is the first actual write.
