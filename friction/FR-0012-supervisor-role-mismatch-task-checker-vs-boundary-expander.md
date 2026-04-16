# FR-0012: Supervisor role drifted toward task checking instead of boundary expansion

Captured: 2026-04-15
Source: principal
Status: mitigated

## What happened

The principal stated that the supervisor still feels like "a task checker and
not a boundary explorer/expander." The deeper complaint was not about one bad
call. It was about role shape: the supervisor was helping, but not reliably
increasing the autonomy and capability of the layer below it.

## Why it matters

If the supervisor only routes, checks, and reminds, then the principal still
has to manage the supervisor and the supervisor still has to manage PMs in a
repeating loop. That is local productivity, not stack progression.

The intended stack behavior is different:

- principal pushes supervisor upward
- supervisor pushes PMs upward
- PMs absorb more recurring work without repeated nudges

Without that compounding effect, the control plane does not create leverage.

## Root cause / failure class

**The charter described orchestration and routing more clearly than managed
autonomy expansion.**

That made it too easy for the supervisor to do useful work while still aiming
too low.

## Proposed fix

1. Make "improve the autonomy of the layer below you" an explicit supervisor
   responsibility in `AGENT.md`.
2. Add a visible pressure surface so items being actively pushed cannot hide in
   transcript memory.
3. Treat repeated PM nudges as a structural problem, not just an execution
   problem.
4. Hold status responses to an output contract that includes what the
   supervisor is doing and what it is pushing the PM layer to do.

## References

- Principal message, 2026-04-15
- `/opt/workspace/supervisor/AGENT.md`
- `/opt/workspace/supervisor/roles/supervisor.md`
- `/opt/workspace/supervisor/pressure-queue.md`
