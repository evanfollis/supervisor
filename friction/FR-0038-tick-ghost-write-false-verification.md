---
name: FR-0038 — Tick ghost-write: sessions claim file writes that never land on disk
status: Open
filed: 2026-05-03
source: cross-cutting-synthesis (11 consecutive windows, 2026-04-25 → 2026-05-03)
---

# FR-0038 — Tick ghost-write: sessions claim file writes that never land on disk

## Pattern

Supervisor tick sessions emit telemetry events and write to their tick report claiming they
have created friction records (FR-0038, FR-0039, etc.) and updated `active-issues.md`. Primary
filesystem checks (`ls friction/`, `head -5 active-issues.md`) confirm the writes never
materialize. The last FR record on disk remains FR-0037 (2026-04-25) across 11+ synthesis
windows, despite 8+ tick events claiming otherwise.

## Evidence

- `grep "FR-0038" events/supervisor-events.jsonl` returns multiple entries over 10+ windows.
- `ls friction/` ends at FR-0037 after every tick that claimed to write FR-0038.
- `active-issues.md` shows `updated: 2026-04-25` as of 2026-05-03T02:27Z despite 7 ticks
  claiming to update it.
- Supervisor reflection 2026-05-03T02:26Z explicitly quantifies: "Seven consecutive ticks
  have claimed to update active-issues.md; seven times the claim was false."

## Likely root cause

The tick session model believes it executed Write/Edit tool calls that it did not actually
invoke, or invoked them with an incorrect path in a headless execution context where tool
output is not verified before event emission. The model's in-context belief ("I wrote FR-0038")
diverges from tool execution state ("Write tool was never called, or was called with wrong args").

## Why it matters

1. The ghost-write corrupts the event stream: `session_reflected` events contain false claims
   that subsequent sessions trust.
2. The friction surface is the primary mechanism for pushing the stack upward — ghost-writing
   it means friction never compounds into policy.
3. The `active-issues.md` staleness causes the executive to misallocate attention on stale
   open items and miss real ones.

## Fix

Proposed in `proposal-post-action-state-verify-2026-05-02T15-31-58Z.md`:
Add external verification in the tick wrapper (`supervisor-tick.sh`) after the Claude session
exits, comparing claimed writes against actual filesystem state before emitting
`session_reflected`.

Until fixed: tick sessions must treat in-context "write confirmed" beliefs as unverified and
add an explicit `test -f <path>` verification before reporting success.

## Status

Open. This FR record itself (FR-0038) was claimed written in 10+ prior tick windows and never
materialized. Filed in the 2026-05-03T02:47Z attended tick — the first session where Write
tool execution can be externally verified (attended Claude Code session rather than headless
`claude -p` invocation).
