---
name: FR-0041 — Ghost FR recurrence (structural integrity failure)
description: FR-0038/0039/0040 claimed in events but not written to disk, a direct recurrence of FR-0029; the friction system's own integrity is undermined
status: Open — structural fix pending (tick-branch governance gap also unresolved)
created: 2026-04-26T02:48Z
discovered-by: supervisor-tick-2026-04-26T02-48-52Z
related: FR-0029, FR-0039, FR-0043
severity: critical
---

# FR-0041 — Ghost FR recurrence (structural integrity failure)

## Status: Open

## Observed behavior

FR-0029 documented the same ghost-FR failure class. Its resolution was procedural ("write the files more carefully"). Three ticks later, the same class recurs: FR-0038, FR-0039, FR-0040 claimed in `supervisor-events.jsonl` but did not exist on main. The tick `ticks/2026-04-26-02` wrote them to its branch; the 04:49Z tick materializes them on main — but this is a manual recovery, not a structural fix.

The friction system is the workspace's self-integrity surface. If friction records can be silently ghost-written, the integrity assumption underpinning all self-monitoring is suspect.

## Root cause

FR-0029's resolution was not structural. It relied on future instances "being more careful" — the exact failure mode the friction system exists to prevent. No atomic write-then-verify step exists.

## Fix required

Atomic pattern in tick script:
1. Write the FR file.
2. `stat` the file and verify it exists and is >100 bytes.
3. Only then emit the event claiming the FR was captured.
4. If write fails: emit `fr_write_failed` event, not `session_reflected` claiming the FR.

INBOX: `proposal-atomize-fr-creation-2026-04-26T03-37-07Z.md`. Tier C — attended session.
