---
name: FR-0039 — Synthesis-to-execution pipeline: 0 of 17 proposals landed in 10 cycles
Status: Open
created: 2026-05-02
source: cross-cutting-synthesis-2026-05-02T03-23-48Z
---

# FR-0039: Synthesis-to-execution pipeline is non-functional

## Observation

As of 2026-05-02, 10 consecutive synthesis cycles have produced
proposals. Zero of those proposals have been implemented. INBOX has grown
from ~15 items (cycle 1) to 40 items (cycle 10). The dispatch obligation
(24h window to dispatch, defer, or close each synthesis proposal) has not
been honored in any cycle.

## Why this matters

The synthesis loop's purpose is to detect systemic friction and route it
to fixes. A synthesis loop that detects without fixing is a passive
observer, not a governing mechanism. The workspace is accumulating a
detailed, accurate diagnosis of itself while making zero progress on the
diagnosed issues.

## Root causes

1. **Tier-C proposals blocked by sandbox**: Most proposals target
   `scripts/lib/`, `CLAUDE.md`, and `decisions/` — all Tier C for tick
   sessions. They require attended operator work that isn't happening.

2. **No dispatch authority for safe Tier-B proposals**: Even proposals
   that could be safely implemented in tick sessions (e.g., updating
   `active-issues.md`, writing new INBOX items) require explicit
   authorization that hasn't been granted.

3. **No attended session triage cadence**: The principal's attended
   sessions haven't been scheduled or triggered to clear the queue.

4. **INBOX saturation degrades signal**: At 40 items, the queue has so
   many proposals that the genuinely urgent ones (401 auth fix,
   reflect.sh bypass, ghost-write diagnosis) lose salience.

## What would resolve this

Either:
A) Attended principal session does bulk triage (even "won't fix" on 30
   items would restore signal quality)
B) Tick sessions are granted explicit authority to implement safe Tier-B
   proposals (requires principal decision / ADR amendment)
C) Scripts/lib and CLAUDE.md changes are treated as "operator-mediated"
   with a clear attended-session playbook triggered by URGENT count

## Status

Open. Structural. Requires attended triage or authority grant.
