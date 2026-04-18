# Project: command

## Current status

- **Highest active pressure.** `command` is supposed to be the principal-facing
  executive control plane, but it still leaks too much mechanism and still
  makes the principal reason about sessions and lanes instead of one trusted
  executive conversation surface.
- The current browser executive surface is still failing its core job: messages
  append, but the principal does not get a live conversational response. In
  practice this means the homepage still behaves like a thin wrapper around a
  dead lane instead of the system's usable point of contact.
- A `command` worker has now implemented the direct-response browser fix on
  disk. The homepage is wired to a real server-side executive turn rather than
  the dead tmux append path. Remaining step: deploy the updated `command`
  service so the live browser reflects it.
- The executive recently relapsed into direct `command` implementation because
  the product incoherence was strategically painful. That is now treated as a
  control-plane failure, not the operating model.
- `command` remains the only governed project that is still not on normal git
  footing (`git rev-parse` fails in the repo), which keeps `/review`
  enforcement structurally weaker there than elsewhere.
- There is still no PM acknowledgment handoff back from `command` for the
  executive-control-plane recentering work. At the control-plane level, the
  pressure has been sent but not yet demonstrably absorbed.

## What needs to change

- The `command` PM must turn the browser into one principal-facing executive
  conversation surface with one canonical top-level lane behind it.
- The `command` PM must close the "message sent but nothing happens" failure as
  a product bug, not as a sessions/tmux debugging artifact.
- `Sessions` should become a debugging/inspection surface, not the principal's
  mental model of how the system works.
- The PM needs to reply explicitly with the design/implementation plan rather
  than leaving the executive to infer progress from browser symptoms.
- The repo needs to absorb the governance baseline:
  - initialize git
  - make review enforcement real
  - document that lack of git is a structural failure, not setup trivia

## Executive stance

- **Shape aggressively, implement exceptionally.** Hold the product and PM to
  the control-plane bar; do not keep "saving" the project from the executive
  lane by default.

## Active artifact links

- PM handoff:
  `/opt/workspace/runtime/.handoff/command-executive-conversation-surface-2026-04-15T19-06Z.md`
- PM handoff:
  `/opt/workspace/runtime/.handoff/command-executive-recenter-command-as-control-plane-2026-04-15T18-36Z.md`
- PM handoff:
  `/opt/workspace/runtime/.handoff/command-pressure-git-bootstrap-and-review-enforcement-2026-04-15T13-53Z.md`
- PM handoff:
  `/opt/workspace/runtime/.handoff/command-acknowledge-executive-surface-gap-2026-04-15T19-16Z.md`
- PM handoff:
  `/opt/workspace/runtime/.handoff/command-fix-broken-executive-conversation-2026-04-15T19-28Z.md`
- PM reply:
  `/opt/workspace/runtime/.handoff/general-command-executive-conversation-fixed-2026-04-15T19-34Z.md`
- Supervisor friction:
  `/opt/workspace/supervisor/friction/FR-0016-command-still-behaves-like-ui-over-sessions.md`
- Supervisor friction:
  `/opt/workspace/supervisor/friction/FR-0018-executive-relapsed-into-project-implementation.md`
