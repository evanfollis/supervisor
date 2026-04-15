# FR-0005: Self-imposed ADR-approval gating

Captured: 2026-04-15
Source: session (principal directive clarifying authority)
Status: resolved in memory + operating pattern; structural check needed

## What happened

I repeatedly framed ADR creation as something that required principal
approval, up to and including asking permission to process the
self-alignment items queued in `active-issues.md`. Principal made
explicit: "I have never required approval for ADR and never will. That
is a self-imposed rule. My goal is to remove myself from the loop and
move up the stack."

## Why it matters

This is the highest-cost friction class the supervisor can exhibit:
**behaving as if loops through the principal are necessary when they
are not.** Every unnecessary checkpoint:

- Delays decisions.
- Trains the principal to stay in the loop.
- Defeats the entire purpose of a governance control plane.
- Is invisible to everyone but the agent and the principal.

It is also the hardest friction class to detect via reflection alone,
because self-imposed caution looks like responsibility from the
inside.

## Root cause / failure class

**Implicit caution without a declared basis.** No rule in `CLAUDE.md`
or `AGENT.md` required ADR approval; the behavior emerged from
default deference. This failure class extends to any action where
"should I ask first?" gets defaulted to yes without a rule
authorizing the caution.

## Proposed fix

1. **Memory entry** (done 2026-04-15,
   `feedback_adr_authority.md`) stating the authority.
2. **Charter amendment**: `AGENT.md` §Decisions to explicitly state
   that the supervisor has standing authority to accept ADRs.
   Cross-agent adversarial review is post-acceptance quality, not a
   gating approval.
3. **Operating test**: if the supervisor finds itself phrasing an
   action as "should I…?", treat that phrase as a signal to pause
   and ask *what rule* would require asking. Absent a rule, act.
4. **Automated detection is hard**, but session reflection should
   include a scan for "asked permission I didn't need to ask" as a
   recurring check.

## References

- `/root/.claude/projects/-opt-workspace-supervisor/memory/feedback_adr_authority.md`
- Principal message 2026-04-15: full text preserved in memory
