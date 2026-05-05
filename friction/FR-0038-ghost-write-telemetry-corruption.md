---
name: FR-0038 Ghost-write telemetry corruption
description: Tick sessions emit friction_captured events naming files that were never committed to main
type: friction
status: Open
created: 2026-05-05
source: supervisor-tick-2026-05-05T02-47-04Z
priority: high
---

# FR-0038: Ghost-write telemetry corruption

## What happened

Tick sessions (2026-05-05T00-49-35Z, 2026-05-04T22-47-40Z, and 8+ prior) emitted `friction_captured` events for `FR-0038-ghost-write-telemetry-corruption.md` and `FR-0039-consecutive-tick-invocation-failures.md`. Commits show the files were never included. The event log is now a false signal — it contains repeated claims of successful friction writes that never landed.

## Evidence

- `git log --all | grep FR-003` — no matching commits
- `ls friction/FR-003[89]*` — files absent despite 8+ event claims
- Most recent tick commits at `50f6ca1` and `c31d4db` contain only `session-summary` and `verified-state.md`

## Root cause

Two contributing factors:
1. Tick sessions were writing to tick branches (not main). Tick branches never merge to main, so Tier-A friction writes on tick branches are silently abandoned.
2. Even when a tick runs on main, the pre-tick autocommit only stages files it finds dirty. If friction files are created after the autocommit checkpoint and before the tick commit, they may still miss the commit window depending on the staging logic.

## Failure class

A tick that claims to write a durable Tier-A artifact but doesn't commit it is indistinguishable from a tick that succeeded. The event log becomes a false signal. Downstream ticks read "already written" from events and skip writing, compounding the miss.

## Fix direction

The tick wrapper's commit step must explicitly stage the friction/ directory before committing. The autocommit job must not be the sole mechanism for persisting within-session Tier-A writes.

## Status

Open. Fix requires change to `scripts/lib/supervisor-tick.sh` (Tier C — attended session).
