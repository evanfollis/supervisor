---
id: FR-0038
title: Ghost-write claims corrupt telemetry truth source
status: Open
created: 2026-05-04
source: supervisor-tick-2026-05-04T10-47-24Z
severity: high
---

# FR-0038: Ghost-write claims corrupt telemetry truth source

## What happened

Ticks run on isolated branches (e.g. `ticks/2026-05-04-04`), not on `main`. When a tick
writes to Tier-A surfaces like `system/active-issues.md` or `friction/FR-NNNN-*.md`, those
writes exist only on the tick branch. The tick then emits a `session_reflected` event into
`events.jsonl` with a note claiming "active-issues updated on main" or "FR-0038 written to
main." These claims are false — the writes never reach `main` unless a merge happens.

Consequence: `events.jsonl` (a charter-designated truth source) contains false state
assertions. Any downstream consumer that trusts those assertions (synthesis, executive
reentry) receives corrupted signal.

## Evidence

Cross-cutting synthesis 2026-05-04T03:26Z, Pattern 2:
> "The 22:47Z tick's `session_reflected` note says 'active-issues updated on main (8d stale fixed)';
> the 00:49Z tick's note says 'FR-0038 written to main.' Both are contradicted by primary checks
> (`active-issues.md:4` still shows `updated: 2026-04-25`; `friction/` tops at FR-0037)."

## Root cause

Tick harness (`supervisor-tick.sh`) creates a new branch per tick, which is correct for
isolation. But ticks write to Tier-A surfaces (active-issues, friction/) assuming those writes
will be visible on `main` — without a merge step. The event note echoes the tick's claim, not
the verified post-merge state.

## Fix needed

Either:
A) Ticks should emit event notes that qualify their writes as "on tick branch" rather than "on main."
B) The tick harness should merge Tier-A writes to main before the event note fires.
C) Ticks should not claim branch-local writes as complete actions in the event log.

Option C is immediate (change the event note template); A and B are structural.

## Related

- Cross-cutting synthesis 2026-05-04T03:26Z, Pattern 2
- `proposal-no-clobber-discipline-2026-04-27T03-30-40Z.md` (INBOX)
- FR-0029 (tick-branch isolation root cause, earlier formulation)
