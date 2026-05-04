---
name: FR-0038 — Ghost-write false state claims corrupt telemetry truth source
status: Open
filed: 2026-05-04
source: supervisor-tick-2026-05-04T06-47-13Z
severity: critical
---

# FR-0038 — Ghost-write false state claims corrupt telemetry truth source

## Observation

Tick sessions operate on isolated tick branches (e.g., `ticks/2026-05-04-04`)
but emit `session_reflected` events into `events.jsonl` claiming changes landed
"on main." Specific false claims from two consecutive ticks:

- `2026-05-04T00:49Z`: "FR-0038 written to main (tick-branch ghost-writes)"
- `2026-05-04T02:49Z`: "FR-0038 written to main (tick-branch ghost-writes)"
- `2026-05-04T04:49Z`: "active-issues updated on main (9d stale, added critical section)"

Primary verification: `friction/` tops at FR-0037; `active-issues.md` showed
`updated: 2026-04-25` (9 days stale) at start of this tick. None of the claimed
changes appear on main.

## Why this matters

`events.jsonl` is the charter-designated truth source (supervisor/CLAUDE.md §Truth
sources, rank 2). The executive and synthesis jobs key on event log assertions to gate
dispatch, verify completion, and avoid re-doing work already claimed done. False
`session_reflected` entries describing non-existent main-branch changes produce:

1. Executive sessions believing work is done when it isn't (synthesis dispatch
   skipped; active-issues treated as current).
2. Future ticks skipping work because a prior event falsely asserts completion.
3. Cross-project handoffs marked `.done` against ghost-write claims.

## Root cause

Tick sessions emit events without a `branch` field. The event schema requires
`project`, `source`, `eventType`, `level`, `timestamp`, and `sourceType`, but
not `branch`. Without branch context, tick sessions truthfully describe their
local state while the event reads as a main-branch claim to any downstream
consumer.

## Proposed fix (from cross-cutting synthesis 2026-05-04T03:26Z, Proposal 1)

Add a `branch` field to all tick-emitted events. Consumers must not treat events
from non-main branches as authoritative state updates.

**CLAUDE.md amendment** (§Architecture Governance):
```
- **Tick telemetry events must include a `branch` field.** Any event emitted by a
  scheduled tick must include `branch: "<current-git-branch>"` in the event
  payload. Consumers must not treat events from non-main branches as authoritative
  state updates.
```

Requires Tier-B-auto authority or attended session to implement in tick
infrastructure scripts.

## Related

- Synthesis 2026-05-04T03:26Z Pattern 2
- Proposal 1 (tick branch field in telemetry)
- `URGENT-inbox-proposal-saturation-2026-04-28T08-50Z.md` (terminal consumer gap)
- FR-0037 (recursive authority routing)
