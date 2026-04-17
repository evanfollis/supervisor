# FR-0026 — PM pauses at cross-repo commit under action-default frame

Status: open
Detected: 2026-04-17T19:40Z
Trigger: skillfoundry PM during execution of `skillfoundry-401-escalation-hook` handoff

## What happened

ADR-0020 landed the action-default contract. The thread-opening frame was
injected into executive threads; project PMs received handoffs with an
explicit `Constraints / non-goals` clause pointing at ADR-0020.

Four PMs were dispatched in parallel. Three shipped cleanly on the first
pass: atlas (`805f264` + `0faa536`), command (`76085db`), mentor
(`2daddb4`). All four commits carried proper why-messages and updated the
relevant CURRENT_STATE.md surfaces.

The fourth, skillfoundry, completed the actual code work — found the
401 escalation hook from a prior tick was dead code (`$SUP` undefined
under `set -u` would crash before the handoff could be written), fixed
it with an S1-P2-compliant `tick.escalated` event and an 8-assertion
test — but then stopped at:

> "Changes are uncommitted across two repos (supervisor + harness).
>  Want me to commit?"

The hesitation was specifically triggered by the change crossing a repo
boundary (supervisor code touched from the harness session). The frame
and contract both say "reversible work ships"; neither explicitly said
"crossing a repo boundary is still reversible."

A single nudge resolved it, but that nudge came from the executive
(me), not the principal. The principal correctly flagged that this is
my feedback loop to close, not theirs.

## Failure class

The action-default contract (ADR-0020) addressed "advice vs action"
at the top level but did not anticipate the **boundary-ask** shape:

- "Is it OK to commit across repos?"
- "Is it OK to edit a file in supervisor/ when my session is rooted in harness/?"
- "Is it OK to update system/active-issues.md from a project tick?"

All three are reversible. All three would be resolved post-hoc by the
friction log or by a supervisor correction if wrong. None of them are
in the "only the principal can decide" class.

The PM was doing what its operating manual told it to — workspace CLAUDE.md
says project sessions "should not edit project code directly" at the
executive layer, and the supervisor charter says the supervisor "never
leaves a project repo dirty." A PM reading those rules concludes boundary
violations warrant caution. The rules are aimed at the executive, not
at PMs doing scoped work that happens to require a cross-repo touch.

## Correction

Two changes, both reversible, both applied this tick:

1. **Frame update (code):** the thread-opening frame now explicitly names
   cross-repo and cross-boundary cases as still shipping, not asking. See
   `projects/command/src/lib/threadConversation.ts::THREAD_OPENING_FRAME`.

2. **Contract update (policy):** ADR-0020 amended with an explicit
   clarification: cross-repo reversible work is still reversible; boundary
   concerns are resolved post-hoc via friction or handoff, not by pausing
   mid-task. The PM handoff template (what I write when delegating) should
   include an explicit "boundary scope: X" line when the work inherently
   crosses a repo so the PM doesn't have to infer it.

## What will tell us this is closed

Next time a PM encounters a task whose cleanest fix crosses a repo
boundary (e.g. a harness bug caused by a supervisor config), it ships
without asking. If another "want me to commit across repos?" turn
appears, the correction above was insufficient and we tighten again.

## Why-this-matters

The whole point of ADR-0020 is to compress supervision work downward.
Each round of "act on PM's behalf, nudge, wait, nudge again" is the
exact work the contract was supposed to eliminate. Capturing this
friction and converting it to policy is how the me→PM loop closes on
its own — same way the user→me loop does.
