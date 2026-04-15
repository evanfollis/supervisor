# ADR-0003: Workspace topology and path indirection

Date: 2026-04-14
Status: accepted

## Context

`/opt/projects` currently plays three different roles at once:

1. Container for managed project repos
2. Root for the supervisor control plane
3. Bucket for runtime state (`.meta/`, `.handoff/`, `.features/`, telemetry)

This makes the directory name misleading and weakens the architecture boundary
between control plane, execution plane, and generated state.

At the same time, the supervisor needs broad visibility across the workspace.
That visibility should not require the supervisor repo to physically contain all
project repos.

## Decision

Adopt a three-surface workspace model:

```text
/opt/workspace/
  supervisor/
  projects/
  runtime/
```

With these meanings:

- `supervisor/` — durable control-plane repo
- `projects/` — managed project repos only
- `runtime/` — generated state and operational scratch

Until the physical move is complete, the current `/opt/projects` layout remains
the active compatibility topology.

To make the move low-risk, all control-plane scripts and units must consume a
shared path layer rather than hardcoding `/opt/projects/...`.

The shared path layer supports two modes:

- `legacy` — current compatibility layout rooted at `/opt/projects`
- `split` — target layout rooted at `/opt/workspace`

## Consequences

### Positive

- Directory names match architectural meaning.
- The supervisor gains explicit authority over the workspace without becoming
  the filesystem parent of every repo.
- Runtime artifacts become disposable and relocatable.
- The physical move becomes a configuration cutover rather than a script rewrite.

### Costs

- There is a transition period where docs and tooling must tolerate both
  topologies.
- Existing scripts, prompts, and systemd units need path abstraction.
- Some historical docs will refer to the old layout until the move is complete.

## Implementation constraints

1. No control-plane script may introduce new hardcoded `/opt/projects/...`
   references except compatibility wrappers and migration docs.
2. Runtime paths must resolve through the shared path layer.
3. The supervisor event schema must be valid before more automation is added.
4. The physical directory move happens only after path abstraction and an audit
   pass are complete.

## Alternatives considered

1. **Keep `/opt/projects` as the permanent mixed-use root.**
   Rejected: preserves the current naming and boundary confusion.

2. **Move all repos under `/opt/supervisor/projects/`.**
   Rejected: collapses governance and managed repos into the same path ancestry.

3. **Put `supervisor/` next to `projects/` but keep runtime state in `projects/`.**
   Rejected: fixes only part of the confusion; generated state still pollutes the
   project namespace.
