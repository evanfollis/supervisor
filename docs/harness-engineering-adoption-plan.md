# Harness Engineering Adoption Plan

## Source

This plan translates Ryan Lopopolo's harness-engineering talk and OpenAI's
Symphony writeup into workspace work. The core lesson is not "use more agents."
It is: make the repo, runtime, and review loop legible enough that agents can
complete work without the principal or executive repeatedly reconstructing
context.

## Current Truth

The workspace already has the philosophical base:

- durable context front doors and progressive disclosure
- recursive delegation from project agents through PMs to the executive
- telemetry, reflection, synthesis, friction records, and adversarial review
- worktree concepts in the supervisor and skillfoundry harness
- command as the principal-facing control plane

The missing layer is executable harness discipline. Too many requirements still
exist as prose, handoffs, or norms instead of being presented to agents at the
moment they need them through checks, review agents, browser evidence, and task
state.

## Target State

Each governed repo should expose enough machine-readable context and runtime
evidence for an agent to:

1. read a small front door and locate deeper sources of truth;
2. run a standard harness check and receive actionable remediation;
3. validate user-facing behavior from the same client surface the principal
   uses;
4. receive role-specific review before merge;
5. work in isolated task/worktree units when concurrency matters;
6. turn repeated failures into docs, checks, or automated reviewers.

## Workstreams

### 1. Agent-Legible Browser And Runtime Evidence

Owner: `command` PM.

First deliverable: install browser automation for command and add real-browser
smoke coverage for `/`, `/attach/general`, `/attach/general-codex`,
`/artifacts`, login, and portfolio expansion. Evidence must include screenshot
or trace artifacts under runtime, not just a pass/fail line.

Why first: command is the front door. It already declares
`browser_capability_missing`; closing that gap unlocks better validation for
every principal-facing workflow.

### 2. Workspace Harness Check

Owner: supervisor.

First deliverable: `workspace.sh harness-check`, backed by
`scripts/lib/harness-check.py`, scanning reflected projects for front doors,
staleness, large instruction blobs, context-load declarations, browser-QA gaps,
QA-plan gaps, and existing check scripts.

Principle: start as report-only, then promote specific checks to strict gates
after one cycle of false-positive review.

### 3. Symphony-Lite Task Orchestration

Owner: `command` PM with supervisor review.

First deliverable: design and ship a local-file orchestrator before adopting an
external tracker. Use existing `runtime/.handoff/`, `runtime/.threads/`, command
task store, and feature worktrees. The issue tracker can be a JSON/Markdown task
ledger until the state machine proves useful.

Required states: `ready`, `running`, `blocked`, `review`, `done`, `deferred`.
Required behavior: bounded concurrency, per-task workspace identity, restart or
stale detection, telemetry, and review packet links.

### 4. Role-Specific Review Agents

Owner: supervisor for role definitions; project PMs for repo-local activation.

First deliverable: promote the existing maintenance-agent model into reviewer
profiles that can run on push/tick:

- reliability reviewer
- security/boundary reviewer
- frontend/browser reviewer
- context/state reviewer
- telemetry/friction reviewer

Review findings must either become accepted tradeoffs, fixes, or new checks.
They must not accumulate as unowned prose.

### 5. QA Plans As First-Class Context

Owner: each project PM.

First deliverable: every user-facing or runtime-active repo gets `docs/QA.md`
or an equivalent local path named in `CURRENT_STATE.md`. It must define critical
journeys, commands, expected artifacts, browser/runtime requirements, and what
counts as enough evidence.

### 6. Harness Garbage Collection

Owner: supervisor, then project PMs.

First deliverable: a weekly playbook that scans recent reviews, reflections,
friction records, and repeated manual corrections, then emits small tasks to
encode the repeated pattern as a doc, check, test, or reviewer.

This is the "garbage collection day" equivalent. The aim is not cleanup as
polish; it is preventing repeated agent failure modes from compounding.

## Execution Order

1. Ship `workspace.sh harness-check` as report-only.
2. Dispatch command browser evidence handoff.
3. Dispatch command Symphony-lite design/build handoff.
4. Add QA-plan requirement to project PM handoffs after the first report.
5. Activate role-specific review profiles once the first two command gaps are
   closed.
6. Run weekly harness garbage collection and promote stable checks to strict.

## Acceptance Gates

- `workspace.sh harness-check` runs from `/opt/workspace` and reports every
  reflected project.
- Command has real-browser evidence for its critical routes.
- At least one task can move through Symphony-lite from `ready` to `review`
  with a task/workspace identity and telemetry.
- A role-specific reviewer produces a durable artifact that causes either a fix
  or an accepted tradeoff.
- Recurrent review/reflection findings produce new harness checks, not just
  new reminders.

## Non-Goals

- No immediate "0 human review" policy.
- No automatic production deploy expansion until browser evidence and review
  packets are reliable.
- No external issue tracker dependency before local state-machine behavior is
  proven.
- No project code edits from the executive surface; project sessions receive
  handoffs and own implementation.

