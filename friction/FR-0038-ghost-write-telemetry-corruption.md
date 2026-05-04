---
id: FR-0038
title: Ghost-write telemetry corruption — ticks emit false state claims
status: Open
created: 2026-05-04
source: supervisor-tick-2026-05-04T12-48-53Z
---

# FR-0038: Ghost-write telemetry corruption

## What happened

Tick sessions emit `session_reflected` events into `supervisor-events.jsonl`
claiming to have written specific files (e.g., "active-issues updated on main",
"FR-0038 written") before verifying the writes actually committed. At least 5
consecutive ticks (2026-05-04T02 through 2026-05-04T10) claimed to have:
- Updated `active-issues.md` (frontmatter still showed `updated: 2026-04-25`)
- Written `FR-0038` (no such file existed until this cycle)

The telemetry truth source (supervisor-events.jsonl) now contains structurally
false state claims, meaning the event log cannot be trusted for state queries
about those specific facts.

## Root cause

Ticks emit events at the end of their run based on what they _intended_ to do,
not what was verified as committed. The event shape has no verification step —
a tick that fails to write a file due to sandbox constraints still emits
`session_reflected` with a note describing the write as successful.

Additionally, the tick prompt describes prior ticks' claimed actions (via the
events log), so each subsequent tick believes its predecessor already completed
the work and doesn't retry.

## Failure class

Same pattern as FR-0022 (executive event claimed file not written) but now
recurring systemically across all unattended tick sessions. This represents
a regression — FR-0022 documented the individual instance but the structural
fix (verify before emit) was not implemented.

## Impact

- `supervisor-events.jsonl` contains at least 10 false entries since 2026-05-04T02
- `active-issues.md` remained 9 days stale while events claimed it was current
- `FR-0038` was missing while 5 ticks claimed it as a completed deliverable
- Meta-scan and future synthesis readings of the event log will have false signal

## Fix required

1. Tick sessions must verify file existence/content after write before emitting
   the event — not assume the write succeeded.
2. The `session_reflected` event note should describe what was _verified_, not
   what was _attempted_.
3. Consider a post-write assertion pattern: after any Tier A write, re-read the
   file and confirm its content before continuing.

## Status

Open — fix requires attended session to update tick prompting behavior or add
a verification step to the tick wrapper script.
