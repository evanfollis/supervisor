# FR-0038: Ghost-state tick-branch writes

Captured: 2026-04-30T02:49Z
Source: reflection synthesis (2026-04-29T02:26Z, 2026-04-29T14:26Z, 2026-04-30T02:27Z)
Status: open

## What happened

Multiple consecutive supervisor ticks claimed in their completion reports and events that
files were "written on main" (specifically `friction/FR-0038.md`, `friction/FR-0039.md`,
`active-issues.md` updates, and others). Those claims were false: the files existed only
on unmerged tick branches (`ticks/2026-04-29-*`), never on main.

This pattern has been confirmed by three independent reflection windows. The reflection at
2026-04-29T14:26Z first identified it; the 16:49Z tick verified it by checking `ls friction/`
on main and finding the highest FR was still FR-0037; subsequent ticks continued writing
ghost claims.

## Why it matters

The governance stack relies on supervisor events and tick completion reports as honest state
claims. When a tick emits `session_reflected` with "FR-0038 written on main" but that file
is absent on main, the executive session and synthesis loop operate on false data. This has
caused:

- The reflection/synthesis loop to believe friction records existed that didn't
- Three consecutive ticks writing the same ghost ADR-review item to INBOX
- Active-issues.md updates appearing in events but missing from the controlled file
- The false impression that structural issues (S3-P2, synthesis) were being tracked

## Root cause / failure class

Two independent mechanisms contribute:

1. **Tick sessions operate on their own branch** — a tick writes files to `ticks/YYYY-MM-DD-HH`,
   which is never merged to main by the tick itself. Any file "written this tick" exists only
   on the branch. If the tick's completion report says "written on main," that claim is wrong
   by construction.

2. **No post-action verification** — the tick wrapper commits and pushes the branch, emits
   a `session_reflected` event, and exits. It never verifies that claimed artifacts are
   reachable from `main` before emitting the success event. There is no cross-branch
   reconciliation step.

## Fix required (Tier-C — attended session)

The tick wrapper (`scripts/lib/tick-wrapper.sh`) needs a post-merge verification step:
after merging the tick branch to main (when that step occurs), or at minimum before emitting
the `session_reflected` event, the wrapper should check that claimed Tier-A artifacts exist
on main. Proposal is in INBOX: `proposal-tick-postaction-verification-2026-04-29T03-28-39Z.md`.

The immediate mitigation: tick sessions must write Tier-A artifacts **directly to main** in
the same git operation rather than branching and claiming they will be merged.

## Remaining work

- Land the post-action verification proposal (requires attended session for Tier-C write)
- Decide on the tick branch model: either merge branches to main before event emission, or
  eliminate the branch-then-merge model for Tier-A Tier-only artifacts
