# FR-0007: Principal had to prompt the supervisor to be assertive

Captured: 2026-04-15
Source: session (principal message: "you cannot be passively waiting
for me to acknowledge any elephants in the room you have been quietly
eyeing")
Status: memory captured; structural escalation open

## What happened

The supervisor produced a neutral, well-shaped "opinion on current
project state" that enumerated open items but did not surface the
biggest durability/trust risks as action items. The principal had to
explicitly prompt: be assertive, name elephants, push. Only after
that did the supervisor raise:

- Supervisor repo had no remote (months-old durability hole)
- `/review` gate sitting unimplemented since yesterday's synthesis
- ADRs queued for a whole synthesis cycle with no movement
- Command project with no git at all
- Mentor status ambiguous

All of those were visible in the reentry bundle. None were promoted
without the prompt.

## Why it matters

The supervisor is the agent whose job includes *not requiring the
principal to prompt it*. The whole point of the control plane is that
it holds items open on behalf of the principal, escalates when
escalation is needed, and drives the loop forward under its own
authority. A supervisor that needs prompting is not doing its job —
it's just reporting state.

This is sibling to FR-0005 (self-imposed approval gating) but
distinct: FR-0005 is about unnecessary asking, FR-0007 is about
unnecessary *waiting*.

## Root cause / failure class

**Default output mode is descriptive, not prescriptive.** When asked
"what's your opinion," the supervisor defaulted to "here is what I
see" instead of "here is what I will do and what you need to do." The
charter emphasizes observation and routing; it under-emphasizes
pressure.

## Proposed fix

1. **Memory entry** (done 2026-04-15,
   `feedback_assertive_push.md`).
2. **Charter amendment to `AGENT.md`**: status-and-opinion responses
   must separate (a) current state, (b) what the supervisor is doing
   now, (c) what only the principal can unblock. Descriptive-only
   replies are incomplete.
3. **Reflection prompt template**: the supervisor reflection variant
   (forthcoming) must include "what did I fail to raise proactively
   this session?" as a first-class section.
4. **Structural**: add a `supervisor/pressure-queue.md` or equivalent
   — items the supervisor has decided to push on until resolved.
   Making the push visible makes dropping it visible too.

## References

- Principal message 2026-04-15, preserved in memory
  `feedback_assertive_push.md`
- Synthesis `cross-cutting-2026-04-14T15-27-01Z.md` (contained
  Proposal 1 sitting unactioned for 24+ hours)
