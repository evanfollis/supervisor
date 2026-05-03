---
name: FR-0041 synthesis-to-execution gap
description: 13+ cross-cutting synthesis cycles, 40+ proposals, 0 implemented. The synthesis pipeline diagnoses correctly but cannot execute because proposals target Tier-C surfaces that no autonomous session can modify.
status: open
created: 2026-05-02
cycles: 13
related:
  - INBOX: URGENT-inbox-proposal-saturation-2026-04-28T08-50Z.md
  - INBOX: proposal-tier-b-auto-authority-2026-05-02T18-50Z.md
  - cross-cutting-2026-05-03T03-24-05Z.md (Pattern 2)
---

# FR-0041 — Synthesis-to-execution gap

## What happened

13 cross-cutting synthesis cycles have run. 40+ proposals sit in
`supervisor/handoffs/INBOX/`. Zero proposals have been implemented autonomously.
INBOX grew from ~15 to ~50 items (reduced to ~31 by 2026-05-03T02:47Z attended tick).

## Why proposals don't land

Proposals predominantly target `scripts/lib/`, charter files (CLAUDE.md), and
existing ADRs — all Tier-C from tick sessions. Only attended or operator sessions
can apply them. Attended sessions have been infrequent.

## Structural blocker

No autonomous authority tier exists between "can write INBOX proposals" and
"can edit scripts/lib/". The Tier-B-auto proposal (INBOX item 4 in principal-decisions
file `2026-05-03T02-47Z-principal-decisions-pending.md`) would create this tier.

## Status

Open. Structural fix: Tier-B-auto authority approval, or a standing attended-session
schedule for applying queued proposals.
