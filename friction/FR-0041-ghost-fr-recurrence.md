---
name: FR-0041 — Ghost FR recurrence (structural integrity failure)
description: FR-0038/0039/0040 claimed in events but not written to disk, a direct recurrence of FR-0029; the friction system's own integrity is undermined
status: Open
created: 2026-04-26T02:48Z
discovered-by: supervisor-tick-2026-04-26T02-48-52Z
related: FR-0029
severity: critical
---

# FR-0041 — Ghost FR recurrence (structural integrity failure)

## Status: Open

## Observed behavior

FR-0029 documented the same ghost-FR failure class. Its resolution was procedural ("write files more carefully"). Three ticks later, the same class recurs: FR-0038, FR-0039, FR-0040 are claimed in `supervisor-events.jsonl` but do not exist in `friction/`. The supervisor-reflection-2026-04-26T02:27Z identifies this as a structural gap, not a one-off.

The friction system is the workspace's self-integrity surface. If the friction system's own records can be silently ghost-written, the integrity assumption that underpins all other self-monitoring is suspect.

## Root cause

FR-0029's resolution was not structural. It relied on future instances "being more careful" — the exact failure mode the friction system exists to prevent. No atomic write-then-verify step exists. No event type distinguishes "FR written successfully" from "FR write attempted."

## Fix required

The structural fix is an atomic pattern:
1. Write the FR file.
2. `stat` the file and verify it exists and is >100 bytes.
3. Only then emit the event claiming the FR was captured.
4. If the write fails: emit `fr_write_failed` event (not `session_reflected` with the FR claimed). Do not count a failed write as a successful capture.

This change touches `supervisor-tick.sh` and possibly `reflect.sh` — Tier C. Requires attended session.

The shorter-term fix for the ghost FRs: this current tick writes FR-0038–FR-0040 as actual files (resolving the gap), setting the baseline to FR-0041 for future ticks.
