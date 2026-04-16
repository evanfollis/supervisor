# FR-0018: Executive relapsed into project implementation instead of shaping the PM layer

Captured: 2026-04-15
Source: principal
Status: open

## What happened

The principal correctly called out that the executive was still trying to be a
"do-it-all" surface and failing at it. In response to visible incoherence in
`command`, the executive intervened directly in project code repeatedly instead
of primarily shaping the `command` PM, clarifying the product architecture, and
holding the acceptance bar through delegation.

## Why it matters

This is a control-plane failure, not just a workflow inefficiency. If the
executive becomes the default implementer whenever something is urgent, then
the PM layer never matures and the principal remains the real integrator. That
destroys the intended leverage of the whole workspace.

## Root cause / failure class

**Urgency silently overrode role discipline.**

The executive treated "important and broken" as sufficient reason to bypass the
PM layer, rather than treating urgency as a signal to increase PM pressure,
architectural clarity, and explicit acceptance criteria.

## Proposed fix

1. Record direct executive implementation of project code as an exception
   requiring explicit justification, not a normal recovery path.
2. When the principal-facing surface is strategically broken, route pressure to
   the PM first and make the acceptance bar explicit before touching repo code.
3. Treat any moment where the principal has to remind the executive not to be a
   "do-it-all" as a friction event against the executive role itself.
4. Push `command` toward a single executive conversation surface so the
   principal does not have to reason about sessions, dispatch plumbing, or lane
   selection.

## References

- Principal message 2026-04-15: "You're still trying to be a do-it-all and
  failing miserably at that."
- Principal message 2026-04-15: "I am really trying to design you so that you
  can operate at a higher level and not just be a mindless implementer."
- `/opt/workspace/supervisor/roles/executive.md`
- `/opt/workspace/supervisor/pressure-queue.md`

