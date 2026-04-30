---
type: URGENT
created: 2026-04-30T08:48Z
source: supervisor-tick-2026-04-30T08-48-45Z
priority: critical
deadline: 2026-04-30T17:00Z
references: runtime/.handoff/general-atlas-pool-rotation-decision-needed-2026-04-29T17-00Z.md
---

# URGENT: Atlas hypothesis pool rotation — decision deadline ~17:00Z today

## Status

The pool-rotation handoff was written 2026-04-29T17:00Z. ~24h window for principal
decision. Current time: 2026-04-30T08:48Z. Deadline: ~17:00Z today (~8h remaining).

## What's blocked

Atlas runner is evaluating only 2 `testing` hypotheses (both BitMEX-dependent, both
stuck). 14 `formulated` hypotheses are never pulled in. All-continue streak: 9 cycles.
Epistemic accumulation has stalled.

## The decision (from the handoff)

**Option A+C (PM-recommended):**
- Add `HypothesisStatus.INFEASIBLE` to the model
- Add `data_sources_available()` feasibility check before promoting to testing
- Each cycle: promote N=1 from `formulated` with available data sources
- Mark the 2 BitMEX hypotheses as `INFEASIBLE` (data source unavailable from Hetzner US)
- Net effect: loop restarts with Bitstamp-compatible hypotheses; BitMEX/Kraken picked up if access is ever provisioned

**Option B:** Manual hypothesis queue management (requires attended session each cycle — defeats autonomous purpose)

**Option C alone:** Only deprecate BitMEX hypotheses — doesn't replenish the testing pool

## What the atlas PM session will do once decided

Nothing until principal responds. The PM is waiting on this handoff. The runner continues
to produce all-continue cycles in the meantime.

## Action required

Reply via handoff to `/opt/workspace/runtime/.handoff/atlas-pool-rotation-decision.md`
with: A / B / C / A+C / other.

The original handoff is at:
`/opt/workspace/runtime/.handoff/general-atlas-pool-rotation-decision-needed-2026-04-29T17-00Z.md`

Delete that file and this one once decided.
