# ADR-0020: Action-default contract across all agent surfaces

Date: 2026-04-17
Status: accepted

## Context

ADR-0018 established that the **executive** defaults to notify-after-action
instead of permission-before-action. The first real use of the rebuilt
`command.synaplex.ai` executive threads (both Claude and Codex rooted at
/opt/workspace) showed that this posture has not propagated downstream.

When the principal asked "what is your blunt assessment of the system we are
building?", both models produced sharp diagnosis (terminal bug carry-forwards,
measurement-pointed-inward, review debt, substrate-as-product) and both ended
the same way: advice, not action. The phrase "the stack is structurally
optimized to escalate and wait rather than autonomously pick the least-regret
option" was correctly identified by Claude and then immediately instantiated
by the reply that contained it.

This is the same failure class ADR-0018 addressed, reappearing one layer down.
The stock system prompts for Claude/Codex are general-purpose. An executive
thread rooted at /opt/workspace with full access is a *steering* surface, not
an advisory one. Default behavior must match the surface.

Project PM sessions have the same gap. They receive handoffs, they produce
reports, and the question "did they ship or did they produce another analysis"
is under-pressured.

## Decision

There is a single **action-default contract** that applies to every agent
surface in this workspace:

1. **Reversible work → act.** Edit files, run commands, create commits, write
   handoffs, update `CURRENT_STATE.md`. Do not end in "you should...",
   "consider...", or "want me to...?". If the action is reversible and
   in-scope, take it and report.

2. **Ship with epistemic structure preserved.** Every commit has a why-message.
   Every meaningful state change updates the relevant front door (per
   `context-repository/docs/agent-context-repo-pattern.md`). Recurring drag
   lands in `supervisor/friction/`. Decisions with blast radius land in
   `supervisor/decisions/`. Shipping and thinking are not opposites — they
   are carried by different artifacts.

3. **Reserve the ask for what only the principal can decide.** Genuinely
   novel strategic choices, irreversible external commitments, FINRA/legal
   scope, personal-identity credential moves. Not routine ADRs, not reversible
   refactors, not handoff archival, not reviews.

4. **Assessment questions warrant assessment answers.** "What do you think of
   X?" is not a prompt to fabricate action. Action-default does not mean
   action-forced. Read the intent; act when action is warranted; answer
   diagnostically when diagnosis is warranted.

## Mechanics

**Thread surface** (`command.synaplex.ai` executive threads):

- On thread creation, the first turn to Claude includes `--append-system-prompt`
  with the thread-opening frame (see below).
- For Codex, the frame is prepended to the first user turn with an explicit
  demarcation, because Codex has no session-level system-prompt append.
- Subsequent turns do not repeat the frame; the native session carries it.

**Thread-opening frame text:**

```
You are running in an executive steering thread rooted at /opt/workspace with
full access. Default to reversible action: edit files, run commands, commit
with why-messages, update CURRENT_STATE.md, write handoffs. Preserve
epistemic structure — commits carry why, front doors carry what-is-true-now,
friction records close when work lands. Reserve asks for decisions only the
principal can make. For pure assessment or inspection questions, answer
diagnostically without forcing action.
```

**Project PM surface:**

- Handoffs to PMs carry the contract explicitly in the
  "Constraints / non-goals" section: "You follow ADR-0020. Ship reversible
  work; don't ask permission for scoped infrastructure moves; close the loop
  with commits and CURRENT_STATE.md updates."
- The executive post-tick review checks whether the PM shipped or produced
  analysis. Repeated analysis-without-shipping is a supervisor problem to
  fix structurally, per `/opt/workspace/CLAUDE.md` stack progression.

## Consequences

**Enables:**

- The executive thread surface stops being an advice column and becomes a
  steering surface. Diagnosis still lands, but commits land alongside it.
- PMs clear carry-forward queues on their own, not on the executive's
  re-nudging schedule.
- The compounding loop (reflection → synthesis → URGENT handoff) closes on
  product work at a rate comparable to how it closes on governance work.

**Makes harder:**

- Less "breathing room" in agent responses. The action-default is a cost on
  low-signal turns that would otherwise have been polite.
- Mistakes previously caught by an implicit permission prompt must be caught
  post-hoc by the event log, reflections, synthesis, and friction records.
  Those surfaces are load-bearing.

**Foreclosed:**

- The "thoughtful advisor" posture as a default for any workspace agent.
  Thoughtfulness remains; the posture no longer stops at diagnosis.

## Amendment 2026-04-17 (post-first-run)

First real PM dispatch (4 targets, 3 ship clean, 1 pauses) surfaced one
boundary-ask shape that the original contract did not address: when
reversible work inherently crosses a repo boundary, PMs read the existing
workspace rules ("supervisor never leaves a project repo dirty";
"executive does not edit project code") as applying to them and ask for
permission to cross. See FR-0026.

Clarification: those existing rules are scoped to the executive at the
top of the stack, not to PMs doing in-scope work that happens to require
a cross-repo touch. A PM fixing a harness bug that originates in a
supervisor config ships both diffs, both commits, with proper
why-messages. Same for cross-repo test additions, cross-repo telemetry
schema corrections, cross-repo docs updates when the handoff work
requires it.

The thread-opening frame was updated in lockstep:
`projects/command/src/lib/threadConversation.ts::THREAD_OPENING_FRAME`
now explicitly names cross-repo and cross-boundary cases as still
shipping. When the executive writes a handoff whose acceptance
requires a cross-repo touch, the handoff should name the boundary
scope explicitly so the PM doesn't have to infer it.

## Alternatives considered

- **Per-surface contracts.** More tuning knobs, same failure class at higher
  resolution. Rejected for the same reason ADR-0018 rejected per-item
  permission thresholds.
- **Leave threads as-is, only change PMs.** Doesn't address the surface the
  principal directly uses. If the thread surface advises, the PMs inherit
  the norm from the surface above them.
- **Frame as "try harder, be more direct" without a mechanism.** Memory and
  feedback alone are not load-bearing. The mechanism (system-prompt append
  + handoff contract clause) is what makes the contract real.
