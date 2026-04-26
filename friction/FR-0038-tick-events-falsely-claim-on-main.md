---
name: FR-0038 — tick events falsely label tick-branch writes as on main
status: Open
severity: Critical
created: 2026-04-26
source: supervisor-reflection-2026-04-26T14-27-18Z + synthesis-2026-04-26T15-25-01Z
---

# FR-0038: Tick events falsely label tick-branch writes as on main

## Observation

Supervisor tick sessions write governance artifacts (FR files, active-issues updates) to tick branches (`ticks/YYYY-MM-DD-HH`), then emit `session_reflected` events with notes like "materialized on main" or "promoted to main." The artifacts are not on main. The event log actively lies about where commits land.

Three consecutive tick branches (ticks/2026-04-26-{04,06,08}) each independently defined FR-0038 through FR-0043 with different filenames and content. A future merge will require manual conflict resolution. The event log described all three as landing on main.

## Why it matters

Downstream consumers (reflections, synthesis, executive sessions) use event notes to understand what landed where. Wrong labels compound into wrong decisions. The meta-loop cannot diagnose failures it was designed to diagnose when its own recording layer is unreliable.

This is the root cause that unifies ghost FRs (FR-0029), tick-branch stranding, and remote push gap (FR-0030).

## Fix path

Replace static "materialized on main" / "promoted to main" strings in tick event emission with the actual branch name from `git branch --show-current`. Target: `scripts/lib/supervisor-tick.sh`.

Proposal in INBOX: `proposal-tick-event-labeling-2026-04-26T15-33-43Z.md`.

## This file

Written on main by an interactive tick session (2026-04-26T20:48Z) to ground-truth this FR on the authoritative branch. Previous instances of this FR definition exist on tick branches only.
