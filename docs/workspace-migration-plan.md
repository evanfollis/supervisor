# Workspace Migration Plan

Date: 2026-04-14
Status: proposed
Owner: supervisor

## Goal

Restructure the host so the filesystem matches the architecture:

- `projects/` means managed project repos only
- `supervisor/` is the durable control-plane repo
- `runtime/` is generated state and operational scratch

This removes the current ambiguity where `/opt/projects` is simultaneously a
repo container, a supervisor substrate, and a runtime state bucket.

## Target topology

Preferred long-term layout:

```text
/opt/workspace/
  supervisor/   # git repo: charter, ADRs, playbooks, skills, docs
  projects/     # git repos only
  runtime/      # generated state, telemetry, worktrees, handoffs, snapshots
```

If introducing `/opt/workspace` is undesirable, the same design works as:

```text
/opt/supervisor/
/opt/projects/
/opt/runtime/
```

This plan assumes the `/opt/workspace/...` layout because it gives one clear
workspace root without making the supervisor the parent of project repos.

## Design principles

1. **Control plane and execution plane stay separate.**
   The supervisor governs projects but does not physically contain them.

2. **Directory names must match their meaning.**
   `projects/` contains projects. Runtime state does not live there.

3. **Authority is explicit, not implied by path ancestry.**
   The supervisor gets access to project repos through policy, inventory, and
   tooling, not because they are children of its repo.

4. **Runtime state is disposable and relocatable.**
   No generated artifacts should be load-bearing merely because of where they
   are stored.

5. **The system must be able to inspect and improve itself.**
   The supervisor should emit events about migrations, audit invariants, and
   synthesize follow-up improvements from those artifacts.

## Target path mapping

Current to target:

```text
/opt/projects/supervisor                -> /opt/workspace/supervisor
/opt/projects/context-repository        -> /opt/workspace/projects/context-repository
/opt/projects/atlas                     -> /opt/workspace/projects/atlas
/opt/projects/command                   -> /opt/workspace/projects/command
/opt/projects/career-os                 -> /opt/workspace/projects/career-os
/opt/projects/skillfoundry              -> /opt/workspace/projects/skillfoundry
/opt/projects/.meta                     -> /opt/workspace/runtime/meta
/opt/projects/.handoff                  -> /opt/workspace/runtime/handoff
/opt/projects/.features                 -> /opt/workspace/runtime/features
/opt/projects/.telemetry                -> /opt/workspace/runtime/telemetry
/opt/projects/.health-status.txt        -> /opt/workspace/runtime/health-status.txt
/opt/projects/systemd                   -> /opt/workspace/supervisor/systemd
/opt/projects/scripts/lib               -> /opt/workspace/supervisor/scripts/lib
```

Notes:

- `context-repository/` remains a managed project repo, not part of supervisor.
- Hidden operational directories move under `runtime/`.
- Workspace infrastructure scripts move under `supervisor/` because they are
  control-plane assets, not project assets.

## Canonical ownership after migration

- `supervisor/`
  - Git-tracked
  - Durable instructions, decisions, playbooks, skills, systemd units, control
    scripts
- `projects/`
  - Git repos only
  - No shared runtime artifacts
- `runtime/`
  - Not git-tracked
  - Handoffs, telemetry, snapshots, worktree metadata, generated reports

## Session model after migration

- Supervisor session:
  - cwd: `/opt/workspace/supervisor`
  - inherits `AGENTS.md` and `CLAUDE.md` from the supervisor repo itself
- Project sessions:
  - cwd: `/opt/workspace/projects/<project>`
- Feature sessions:
  - cwd: `/opt/workspace/runtime/features/<project>/<slug>`
- Global inventory:
  - `/opt/workspace/supervisor/config/sessions.conf`
  - `/opt/workspace/supervisor/config/projects.conf`

This removes the current need for `/opt/projects/CLAUDE.md` to act as both
workspace umbrella and supervisor entrypoint.

## Required policy changes

The migration should land together with these policy clarifications:

1. Root-level supervisor discovery must happen at `supervisor/`, not at the old
   mixed-use workspace root.
2. The supervisor may read all managed repos but should only mutate:
   - its own repo
   - runtime state
   - workspace infrastructure paths explicitly designated as control-plane
3. Project code mutation remains a project-session responsibility unless an ADR
   explicitly grants a special exception.
4. Feature sessions opened from the supervisor must carry an explicit mode:
   `coordination` or `implementation`.
   The default for supervisor-opened features should be `coordination`.

## Implementation phases

### Phase 0: Freeze the contract

Purpose: define the intended architecture before moving paths.

Steps:

1. Record an ADR for the new workspace topology.
2. Define canonical variables:
   - `WORKSPACE_ROOT=/opt/workspace`
   - `SUPERVISOR_ROOT=/opt/workspace/supervisor`
   - `PROJECTS_ROOT=/opt/workspace/projects`
   - `RUNTIME_ROOT=/opt/workspace/runtime`
3. Update the supervisor charter to treat accepted ADRs as higher authority than
   syntheses and reflections.
4. Define the runtime event schema for migration events.

Deliverable:

- A stable path contract that tooling can target during the move.

### Phase 1: Make paths configurable before moving anything

Purpose: eliminate hardcoded `/opt/projects/...` assumptions while the old layout
still exists.

Steps:

1. Introduce a shared path library in supervisor infrastructure, for example:
   `supervisor/scripts/lib/workspace-paths.sh`
2. Refactor all workspace scripts and timers to read from those variables.
3. Refactor systemd units to pass environment variables or source an env file.
4. Update maintenance, reflection, synthesis, session-supervision, and
   feature-session scripts to use logical roots rather than absolute old paths.
5. Add a migration audit command that reports any remaining `/opt/projects`
   hardcoded references.

Deliverable:

- The system works unchanged in the old layout, but path selection is now
  indirect and relocatable.

### Phase 2: Separate control-plane assets from runtime state in-place

Purpose: reduce conceptual coupling before the physical move.

Steps:

1. Create new directories under the current tree:
   - `/opt/projects/supervisor/scripts/`
   - `/opt/projects/supervisor/systemd/`
   - `/opt/projects/runtime/` or temporary equivalents
2. Move control-plane scripts and unit files under `supervisor/`.
3. Move `.meta`, `.handoff`, `.features`, `.telemetry`, and
   `.health-status.txt` under `runtime/`.
4. Leave compatibility symlinks from old locations to new ones.
5. Verify all scheduled jobs still work through the compatibility layer.

Deliverable:

- The logical separation exists before the top-level directory move.

### Phase 3: Create the new top-level layout

Purpose: establish the final workspace shape with minimal service interruption.

Steps:

1. Create:
   - `/opt/workspace/supervisor`
   - `/opt/workspace/projects`
   - `/opt/workspace/runtime`
2. Move the supervisor repo into `/opt/workspace/supervisor`.
3. Move project repos into `/opt/workspace/projects`.
4. Move runtime artifacts into `/opt/workspace/runtime`.
5. Replace `/opt/projects` with a compatibility symlink to
   `/opt/workspace/projects` only if needed for legacy project-local tooling.
6. Do **not** recreate a mixed-use `/opt/projects` root.

Deliverable:

- The filesystem now matches the architecture.

### Phase 4: Rebind sessions and automation

Purpose: point the live system at the new roots.

Steps:

1. Update `sessions.conf` and any project inventory files to new cwd values.
2. Update systemd units for:
   - persistent project sessions
   - supervisor session
   - reflection and synthesis
   - server health and maintenance
3. Update tmux launch paths.
4. Restart only the control-plane services first.
5. Then roll project sessions one at a time.
6. Verify that all latest-pointer files and handoff drops land in
   `/opt/workspace/runtime`.

Deliverable:

- The active runtime uses the new paths, not the compatibility layer.

### Phase 5: Remove compatibility shims

Purpose: make the new design real rather than permanently emulated.

Steps:

1. Delete old symlinks once all audits pass for at least one week.
2. Remove fallback path logic from scripts.
3. Remove stale references from docs and playbooks.
4. Add a guard that fails CI or maintenance checks if new hardcoded
   `/opt/projects/` control-plane references appear.

Deliverable:

- No remaining architectural ambiguity.

## Migration cutover sequence

Recommended execution order for the actual move:

1. Pause non-essential timers.
2. Capture a fresh runtime snapshot.
3. Stop session-supervision units.
4. Move supervisor assets.
5. Move runtime assets.
6. Move project repos.
7. Update env files and systemd units.
8. Reload systemd.
9. Start supervisor session only.
10. Verify supervisor reentry and maintenance flows.
11. Start project sessions one by one.
12. Re-enable timers.
13. Run post-cutover audit.

## Verification checklist

After cutover, verify:

1. `general` starts in `/opt/workspace/supervisor`
2. project sessions start in `/opt/workspace/projects/<name>`
3. feature sessions create worktrees under `/opt/workspace/runtime/features`
4. nightly maintenance writes into `/opt/workspace/runtime/meta`
5. handoffs land in `/opt/workspace/runtime/handoff`
6. no control-plane script still writes into a project repo
7. no systemd unit still references `/opt/projects/...` except explicit legacy
   compatibility shims
8. the supervisor can still read all project repos
9. the supervisor event log matches its own schema

## Iterative self-improvement loop

The new architecture should improve itself through explicit artifacts.

Add these mechanisms:

1. **Migration audit event stream**
   Emit events such as:
   - `migration_started`
   - `migration_step_completed`
   - `migration_verification_failed`
   - `migration_completed`

2. **Invariant checker**
   A scheduled supervisor check that asserts:
   - `projects/` contains only repos
   - `runtime/` is non-git and contains generated state only
   - control-plane assets live only under `supervisor/`
   - event schema matches the charter

3. **Path-drift detector**
   Search control-plane code for forbidden hardcoded legacy paths and drop a
   supervisor handoff when found.

4. **Supervisor reflection input**
   Include migration events and invariant-check output in the supervisor’s own
   reflection/synthesis loop.

5. **ADR pressure test**
   Any future topology change requires an ADR plus adversarial review from the
   opposing agent before rollout.

## Risks

1. **Hidden path assumptions**
   Many scripts and unit files currently assume `/opt/projects`.
   Mitigation: Phase 1 path abstraction before any move.

2. **Session restart confusion**
   Live tmux and systemd state may hold stale cwd assumptions.
   Mitigation: controlled restart order and one-session-at-a-time validation.

3. **Project tooling pinned to old paths**
   Some repo-local scripts may assume sibling paths under `/opt/projects`.
   Mitigation: temporary compatibility symlinks and audit reports.

4. **Supervisor overreach remains policy-only**
   Even after relocation, the supervisor could still mutate project code unless
   tooling enforces the boundary.
   Mitigation: add explicit session modes and path guards in feature tooling.

## Recommended immediate next steps

1. Record an ADR adopting the `/opt/workspace/{supervisor,projects,runtime}`
   topology.
2. Refactor workspace scripts to consume shared path variables.
3. Fix the supervisor event schema mismatch before adding more automation.
4. Add a migration audit command to find hardcoded legacy paths.
5. Only then schedule the physical move.
