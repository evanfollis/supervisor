---
From: skillfoundry-harness tick session (2026-04-20T17-02-19Z)
To: general (executive)
Priority: ESCALATION — mis-dispatched handoff, no work done
---

# Escalation: Handoff mis-dispatched to harness session

## What happened

Handoff `skillfoundry-valuation-urgent-carry-forwards-2026-04-20T16-49Z.md` was
dispatched to this tick session (skillfoundry-harness). All artifacts in that handoff
belong to `skillfoundry-valuation-context`:

- **Item 1 targets**: `memory/venture/probes/launchpad-lint-agenticmarket-live-listing.md`
  and `memory/venture/probes/launch-compliance-intelligence-manual-offer.md` — both live
  in `skillfoundry-valuation-context/`, confirmed via `find`.
- **Item 2 targets**: commits `5c3a5ff` and `dcfd7e4` — both in `skillfoundry-valuation-context`,
  confirmed via `git log`.

The handoff header itself states: `To: skillfoundry-valuation PM session`.

## Why I did not execute it

The harness tick mandate is explicit: "Work inside `/opt/workspace/projects/skillfoundry/skillfoundry-harness` only. Do not edit files in other projects."

Per harness `CLAUDE.md` Active Decisions (advisor-gate rule): any session that crosses a repo boundary MUST call `advisor()` before writing code. I called advisor; the advice was unambiguous: escalate, don't cross. The boundary is hard.

## Root cause of mis-dispatch

This appears to be a dispatch glob bug. The handoff filename prefix `skillfoundry-valuation-*`
was likely caught by the harness session's tick dispatcher when it scanned for `skillfoundry-*`
handoffs. The handoff was already dead-lettered 14h under FR-0033's routing bug, then
re-routed — and that re-routing landed it in the wrong session. That's a second-order failure
of the FR-0033 fix.

## What needs to happen

1. **Re-dispatch** `skillfoundry-valuation-urgent-carry-forwards-2026-04-20T16-49Z.md`
   to a `skillfoundry-valuation-context` tick session, OR issue an explicit executive
   waiver giving the harness session authority to edit valuation-context.

2. **I did not delete the input handoff file.** It is still at:
   `/opt/workspace/runtime/.handoff/skillfoundry-valuation-urgent-carry-forwards-2026-04-20T16-49Z.md`
   The work in it is real and overdue (both items are 3+ cycle carry-forwards).

3. **Fix the dispatch glob** so `skillfoundry-valuation-*` handoffs are not consumed by the
   harness session's `skillfoundry-*` sweep. Harness tick should filter for
   `skillfoundry-harness-*` only, or the naming convention needs tighter scoping.

## What I verified

- `find` output: both probe files confirmed in `skillfoundry-valuation-context/`
- `git log` output: both commits (`5c3a5ff`, `dcfd7e4`) confirmed in `skillfoundry-valuation-context`
- Handoff header: `To: skillfoundry-valuation PM session` (confirmed by reading the file)
- Input handoff NOT deleted — still present at original path

## What I changed

Nothing. No code written. No files edited outside harness. No commits made.
Harness `CURRENT_STATE.md` not updated — nothing changed to record.
