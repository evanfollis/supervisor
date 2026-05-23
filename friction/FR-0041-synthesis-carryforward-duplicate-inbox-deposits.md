---
id: FR-0041
title: Synthesis carry-forward creates duplicate INBOX items instead of updating existing ones
status: open
filed: 2026-05-14T16:47Z
source: supervisor-tick-2026-05-14T16-47-20Z
---

# FR-0041: Synthesis carry-forward creates duplicate INBOX deposits

Captured: 2026-05-14T16:47Z
Source: supervisor-tick-2026-05-14T16-47-20Z
Status: open

## Observed behavior

Each synthesis cycle that "carries" a proposal creates a new INBOX file with a new
timestamp (e.g., `proposal-project-local-dispatch-2026-05-14T15-33-41Z.md`) even when
an identical proposal is already present in INBOX (e.g., from `2026-05-14T03-31-27Z.md`).
Current INBOX examples:
- `proposal-project-local-dispatch-*` × 2 (timestamps 03:31 and 15:33)
- `proposal-reflect-sh-dirty-tree-*` × 3 (cycle-33, cycle-34, cycle-35 variants)

## Impact

INBOX grows 2–5 items per cycle without any increase in resolution capacity. At 18 items
(2026-05-14T16:47Z), the queue has crossed the 10-item saturation threshold. Duplicate
items increase the cognitive load of every INBOX review without adding new information.

## Root cause

The tick dispatcher has no deduplication logic. When synthesis marks a proposal as
"CARRIED" and the tick generates an INBOX file, it does not check whether a file with
the same proposal slug already exists.

## Fix direction

Tick dispatcher should check for an existing INBOX file whose name contains the same
proposal slug before creating a new one. If a match exists, skip the deposit (log it
as "suppressed duplicate"). This is lower-scope than Proposal 5 from cycle-36 synthesis
(which proposes a blanket saturation pause). Both fixes are independently useful.

## Related

- Cycle-36 synthesis Proposal 5 (saturation pause): `proposal-inbox-saturation-deposit-pause-2026-05-14T15-33-41Z.md`
- Cycle-35 synthesis Proposal 3 (inbox-dedup.sh): `proposal-inbox-dedup-2026-05-14T03-31-27Z.md`
- Ghost-write cascade CRITICAL in active-issues.md (duplicate symptoms for writes to main)
