# FR-0016: Command still behaves like UI-over-sessions instead of a real executive control plane

Captured: 2026-04-15
Source: principal
Status: open

## What happened

The principal called out that the system still feels like "chasing you around
doing overly literal tasks" and explicitly warned against "polish a turd"
behavior.

The concrete trigger was `command`: while useful slices had been added
(capability attestation, recovery actions, executive-codex ensure, cleaner UI
language), the interaction model still leaked low-level implementation seams:

- `Sessions` and `Orchestrate` diverged in their Codex mental model
- the system drifted toward page/chrome cleanup while the more important
  control-plane incoherence was still present
- the principal was still required to reason about internal mechanism instead
  of trusting one stable high-level executive surface

## Why it matters

This is exactly the failure mode the principal is trying to escape. If the
system keeps converting strategic intent into a series of local fixes, the
principal remains the integrator and escalation engine.

That means the stack is not truly moving upward. It is just getting more
featureful while keeping the same supervision burden.

## Root cause / failure class

**The system is still too willing to optimize local surfaces before proving the
control-plane abstraction is correct.**

In other words:

- too much "make this page nicer"
- not enough "is this actually the right top-level abstraction?"

This is sibling to FR-0015 but deeper. FR-0015 was about overstating
completion. FR-0016 is about aiming at the wrong local optimum: UI coherence
without enough control-plane coherence.

## Proposed fix

1. Treat `command` as a control-plane product first and a UI second.
2. Hold all new `command` work to a stricter test:
   - does this reduce principal supervision burden?
   - does this remove mechanism leakage?
   - does this collapse multiple surfaces onto one true abstraction?
3. Keep pressure on replacing "UI over tmux/session utilities" with:
   - one canonical task model
   - one canonical executive lane model
   - one canonical delegation / observation / recovery model
4. When a surface still leaks internal mechanism, prefer architectural repair
   over presentation cleanup.

## References

- Principal message, 2026-04-15: "Please don't just try to polish a turd."
- Principal message, 2026-04-15: "I feel like I am just chasing you around
  doing overly literal tasks..."
- `/opt/workspace/projects/command/`
- `/opt/workspace/supervisor/friction/FR-0015-partial-front-door-sold-as-finished-control-plane.md`
