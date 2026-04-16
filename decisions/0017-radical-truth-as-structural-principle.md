# ADR-0017: Radical truth as a structural, not aspirational, principle
Date: 2026-04-16
Status: accepted

## Context

The workspace has quality principles in CLAUDE.md ("no bandaid fixes",
"primary evidence first") but these are phrased as behavioral guidance. They
rely on each agent choosing honesty in every session. This breaks in the
automated tick loop because:

- Headless sessions don't have a human present to catch overconfident reports
- Completion reports are self-assessed — the same agent that did the work
  writes the report that the executive reads
- An agent under implicit time pressure (long handoff, complex codebase) will
  summarize optimistically unless the format forces otherwise
- False signal compounds: the executive routes the next handoff based on what
  the completion report claims, not what actually happened

Four cycles of synthesis identified this as a systemic gap: the governance
infrastructure is sound, but execution quality is unverifiable because agents
report what they believe happened, not what they can demonstrate happened.

The principal explicitly named radical truth (honesty with self, other agents,
and the principal) as a first-class requirement, and named the distinction
between structural constraints vs. aspirational principles.

## Decision

**Radical truth is a format requirement, not a character requirement.**

Concretely:

1. **Every completion report must have an Evidence section** containing actual
   command output, commit SHAs, test results — not prose descriptions of what
   the agent did. A completion report with an empty Evidence section is
   structurally incomplete, not just low-quality.

2. **Every completion report must have an Uncertainty section** explicitly
   naming what wasn't tested, what was assumed to work, what might fail.
   An empty Uncertainty section on a non-trivial task is a red flag, not a
   sign of success.

3. **Every completion report must have a Pushback section** where the agent
   names anything about the handoff spec that was wrong, underdefined, or in
   tension with the project's design. Silent execution of a bad spec is a
   failure to communicate, not compliance.

4. **Every project maintains a `CURRENT_STATE.md`** that is updated every tick.
   This is the breadcrumb system. The tick prompt injects it; the agent updates
   it; the next agent reads it. Accuracy is enforced by the format (explicit
   "What bit the last session" and "Known broken or degraded" sections).

5. **The tick prompt explicitly names the failure mode** — overconfident reports
   creating false signal that compounds downstream — so the agent has the
   causal chain in front of it, not just an injunction to be honest.

6. **These requirements propagate to the executive layer.** The executive must
   be as honest with the principal as project PMs are with the executive.
   There is no level of the stack at which comfortable-sounding uncertainty
   is acceptable.

## Consequences

- Completion reports become auditable artifacts, not self-descriptions
- Escalations become the correct response to genuine uncertainty (not a failure
  signal)
- The principal can verify claims by reading Evidence sections, not by
  replaying the entire session
- Agents that are being honest about limitations become structurally
  distinguishable from agents that are being optimistic

## Implementation

- `supervisor-project-tick-prompt.md` rewritten with radical truth framing and
  structured report format (Evidence, Uncertainty, Pushback required sections)
- `CURRENT_STATE_TEMPLATE.md` defines the breadcrumb format with explicit
  "What bit the last session" and "Known broken" sections
- `reflect-prompt.md` updated to maintain (not just append to) CURRENT_STATE.md
- Workspace `CLAUDE.md` updated with "Quality: Radical Truth" section
- Per-project `CURRENT_STATE.md` seeded for active projects

## Alternatives considered

**Stronger model steering via system prompts**: Rejected. Behavioral guidance
is exactly what we're trying to move away from. Formatting requirements are
more robust than injunctions.

**External verification pass**: Worth pursuing as a follow-on (a separate tick
pass that reads completion reports and checks them against git diffs). Not
blocking this ADR.

**Agent scoring / track record**: Interesting longer-term mechanism. Requires
infrastructure not yet built. Deferred.
