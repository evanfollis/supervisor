---
id: FR-0038
title: Tick events falsely claim commits landed on main when they land on tick branches
severity: CRITICAL
created: 2026-04-27
status: Open
source: supervisor-tick-2026-04-27T06-48-08Z (written on main; prior instances on tick branches)
---

# FR-0038 — Tick event labels claim "main" for tick-branch commits

## Observation

Supervisor tick sessions emit `session_reflected` events with notes like
"materialized on main" or "promoted to main" for FR files and other Tier-A
artifacts. These commits actually land on the current tick branch
(e.g. `ticks/2026-04-26-18`), not on `main`. The event record actively lies
about artifact location.

## Evidence

- FRs claimed "on main" in events.jsonl across ticks/2026-04-26-{18,20,22} and
  ticks/2026-04-27-02 — none exist in `friction/` on main until this tick.
- `git branch --contains <sha>` shows commits in tick branches only.
- `active-issues.md` on main still dated 2026-04-25 despite ticks claiming updates.
- This is the 12th+ instance of the ghost-FR pattern (FR-0029 filed 2026-04-22).

## Root cause

`supervisor-tick.sh` event-emission code hard-codes "main" as a convenience
label in the `session_reflected` note string. It never reads the actual current
branch at commit time. The static string propagates into events.jsonl, making
downstream consumers believe Tier-A changes are on main when they are not.

## Impact

- Ghost FRs: valid friction observations filed on tick branches, never visible
  on main, never acted on.
- False active-issues.md update claims: downstream sessions read stale state.
- Compounding: every consumer (reflections, synthesis, executive) trusts events
  over file inspection, so the lie propagates through the entire meta-loop.

## Fix path

In `supervisor-tick.sh`, at the event-emission step:
```bash
ACTUAL_BRANCH=$(git -C "$REPO" branch --show-current)
```
Substitute `$ACTUAL_BRANCH` into the `session_reflected` note. One-line change.
Tier-C (requires attended session edit to scripts/lib/supervisor-tick.sh).
