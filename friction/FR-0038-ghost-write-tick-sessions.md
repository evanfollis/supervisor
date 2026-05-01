---
id: FR-0038
title: Ghost-write pattern — tick sessions emit write-success events without disk evidence
status: Open
created: 2026-05-01
source: supervisor-tick-2026-05-01T16-48-26Z
severity: high
recurrence: 9+ synthesis windows
---

# FR-0038: Ghost-write pattern in tick sessions

## What happened

Ticks at 04:49Z, 06:49Z, and 08:49Z on 2026-05-01 each emitted telemetry events claiming
`FR-0038` and `FR-0039` were written to `supervisor/friction/`. The events stated
"verified on disk after write." `ls friction/` shows FR-0037 as the highest file.
The claimed writes did not land. This is the 9th synthesis window documenting this pattern.

## Root cause (undiagnosed)

Unknown. Candidates: Write tool silently fails in EROFS/sandboxed tick environment;
path is wrong (relative vs absolute); filesystem permissions block writes in some tick
execution contexts. The mechanism has not been diagnosed interactively.

## Impact

- Event model is not a truth source. Any consumer trusting events without primary
  file verification draws false conclusions.
- The ghost-write problem is self-referential: prior ticks tried to capture this
  friction and produced ghost-writes of the friction record itself.
- Active-issues, INBOX, and carry-forward gates downstream of events are unreliable.

## Proposed fix (from synthesis Proposal 4)

Post-write `test -f <path>` verification in tick wrapper before emitting the success event.
If `test -f` fails, emit a failure event and escalate rather than claiming success.
Fix lives in `scripts/lib/` (Tier-C — attended executive session required).

## References

- cross-cutting-2026-05-01T15-28-00Z.md §Pattern 2
- supervisor-reflection-2026-05-01T14-39-10Z.md O1
