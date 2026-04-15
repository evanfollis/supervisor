# Recursive Delegation Stack

The workspace is governed as a recursive stack, not as a flat swarm of agents.

## Core statement

Each layer should absorb routine ambiguity from the layer below, convert stable
resolutions into explicit policy, and escalate upward only what remains novel,
cross-cutting, or consequential.

Escalation flows upward. Policy flows downward.

## Layers

### 1. Project agent

The local worker inside a single repo or feature worktree.

Responsibilities:

- execute work already within delegated scope
- leave legible traces of decisions and failures
- escalate when blocked by ambiguity, authority limits, or cross-project impact

### 2. Project-manager agent

The local governor for one project.

Responsibilities:

- review project-agent output and friction
- turn repeated project-specific judgment into local policy
- keep project behavior coherent across sessions and time
- escalate to the workspace supervisor when issues become cross-project,
  architectural, or authority-expanding

### 3. Workspace supervisor / meta agent

The first governor above the projects. In this workspace, that is the
`general` session and any workspace-root supervisory session acting from
`/opt/workspace` or `/opt/workspace/supervisor`.

Responsibilities:

- aggregate signals across projects
- normalize direct human interventions into legible traces
- route escalations to the right project or to the human principal
- convert repeated cross-project resolutions into workspace policy,
  playbooks, and guardrails

### 4. Human principal

The final governance layer.

Responsibilities:

- set policy and architectural direction
- ratify authority expansion
- resolve consequential exceptions
- decide which governance burdens should remain human-owned

## The governing loop

Every layer performs the same three functions:

### Operate

Handle work already within current delegated authority.

### Govern

Observe where the lower layer drifts, thrashes, surprises, or succeeds.

### Promote

Convert repeated successful handling into policy, workflow, or expanded
delegation for the lower layer.

## What the stack optimizes for

The point is not to minimize escalation at any cost.

The point is to improve the altitude and quality of escalation:

- fewer low-value escalations
- more legible escalations
- tighter downward policy flow
- less reconstruction effort at higher layers

## Control-plane implications

This architecture requires:

- durable truth surfaces outside prompt windows
- explicit role identity for sessions
- append-only traces for direct human intervention
- a promotion path from repeated resolution to binding policy

Without those, the stack collapses back into ad hoc operator memory.
