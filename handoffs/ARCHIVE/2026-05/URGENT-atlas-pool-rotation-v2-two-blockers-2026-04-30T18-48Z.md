---
type: URGENT
created: 2026-04-30T18:48Z
source: supervisor-tick-2026-04-30T18-48-33Z
priority: critical
supersedes: URGENT-atlas-pool-rotation-deadline-2026-04-30T08-48Z.md
references:
  - runtime/.handoff/general-atlas-pool-rotation-v2-with-signal-drift-2026-04-30T17-00Z.md
  - cross-cutting-2026-04-30T15-26-46Z.md §Proposal 4
---

# URGENT: Atlas runner frozen ~18h — TWO independent blockers, decision now overdue 2h

## Status

Pool-rotation decision first requested 2026-04-29T17:00Z. Deadline elapsed
2026-04-30T17:00Z (~2h ago). Runner frozen since 00:45Z today (~18h total).

The v2 handoff at the reference path supersedes the original options A/B/C.

## The two blockers (independent — solving one doesn't solve the other)

**Blocker 1 — BitMEX/Kraken data unavailable (known since 04-29)**
2 `testing` hypotheses require funding-rate data unavailable from Hetzner US.
Perpetual `continue` decisions since 04-29.

**Blocker 2 — Signal-hash drift (newly identified in synthesis 04-30T15:26Z)**
12 `formulated` hypotheses have claim text with parameter values from Apr 18–19.
Current signals find the same patterns with different measurements → different
claim hashes → formulated pool is structurally unreachable. Empty candidate
list → early exit → 0 hypotheses tested.

## Decision matrix

| | Solve B1 | Solve B2 | Code complexity |
|---|---|---|---|
| A (auto-promote with feasibility check) | ✓ | ✗ | Low |
| C (deprecate stuck hypotheses) | partial | ✗ | Near-zero |
| D1 (fallback to formulated, default to Bitstamp) | ✗ | ✓ | Medium |
| D2 (fallback to formulated, refuse if data source unconfirmed) | ✗ | ✓ | Medium |
| A+C+D2 (atlas PM recommendation) | ✓ | ✓ | Medium-high |

**Atlas PM recommendation: A+C+D2**
- A+C closes Blocker 1; INFEASIBLE status prevents future stuck-testing.
- D2 closes Blocker 2 conservatively — hypotheses tested only against
  confirmed-available datasets. Orphaned hypotheses get marked INFEASIBLE
  and a fresh generation pass creates new ones with current parameter values.
- D1 alternative: cheaper but risks testing hypotheses against wrong datasets.

## Monitoring note (already fixed, no action needed)

`9708867` (deployed 14:29Z) patched the S3-P2 gate to detect empty-cycle
freezes within 3 cycles. Future freezes of this class will surface quickly.

## Action required

Reply to atlas PM via handoff at:
`/opt/workspace/runtime/.handoff/atlas-pool-rotation-decision.md`

One line: pick from "A+C+D2", "A+C+D1", "B+D1", "A+C only", or "other".

Atlas PM will execute in the next session.

Delete both this file and `URGENT-atlas-pool-rotation-deadline-2026-04-30T08-48Z.md`
once decided (the old one is being moved to ARCHIVE by the 18:48Z tick).
