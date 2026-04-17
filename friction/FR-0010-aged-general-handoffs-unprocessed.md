---
type: friction
id: FR-0010
slug: aged-general-handoffs-unprocessed
date: 2026-04-15
severity: medium
status: open
resolved_note: Recurring pattern; currently tracked via tick age-check gate (added ADR-0014). Not structurally closed.
---

# FR-0010: Seven general runtime handoffs aged >20h without supervisor action

## What happened

At the 2026-04-15T10:48 tick, seven handoffs addressed to `general` were found in `/opt/workspace/runtime/.handoff/general-*`:

- `general-server-maintenance-2026-04-14T14-55-47Z.md` (~20h old)
- `general-server-maintenance-2026-04-14T15-04-24Z.md` (~20h old)
- `general-server-maintenance-2026-04-15T01-25-29Z.md` (~9h old)
- `general-server-maintenance-schedule-2026-04-14T14-57-37Z.md` (~20h old)
- `general-server-maintenance-schedule-2026-04-14T15-06-29Z.md` (~20h old)
- `general-server-maintenance-schedule-2026-04-14T15-10-00Z.md` (~20h old)
- `general-synthesis-2026-04-14T15-27-01Z.md` (~20h old)

Several of these encode the same maintenance request (patch + reboot, 2026-04-15 08:00-09:00 window). The tick identified and processed them, but the prior attended session left them unread.

## Why it matters

The supervisor's reentry protocol (step 7) says "list handoffs addressed to `general`" — this implies reading and acting on them, not just listing. Six of these predate the tick deployment (ADR-0014 at 2026-04-15T03:55), so there was no automated catch. But the attended session that ran at 03:55 also did not clean up these files.

## Rule signal

Runtime handoffs have no automated age-alarm outside the tick. If the tick is skipped (as happened at 04:48, 06:49, 08:48 due to Codex sessions being active), runtime handoffs can age indefinitely. The tick interlock (skip if session active) is correct for safety but creates a coverage gap for unread handoffs.

**How to apply:** The tick should always process general runtime handoffs even when it would otherwise skip reflection work. Consider making handoff-processing a non-skipable phase in the tick interlock design.
