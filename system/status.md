# System Status

## Role

This supervisor repo is the workspace control plane. Its working context should
represent the best current understanding of the system, not a log of
interactions.

## Current operating model

- `system/`, `projects/`, and `roles/` are the primary working-context
  surfaces.
- `decisions/`, `docs/`, `playbooks/`, `skills/`, and `ideas/` are reference
  layers and promotion targets.
- `runtime/` holds raw activity, telemetry, reflections, synthesis, and other
  derived or append-only evidence.
- `git history` is the state-transition log for this repo.
- `session_id=<id>` in commit messages is the intended provenance bridge from
  context-repo state changes to transcript rationale.
- `workspace.sh context` is the preferred way to load the canonical current
  context bundle in one pass.

## Active focus

- Keep the supervisor substrate current-state-first and resist drift back
  toward archive-heavy working context.
- Correct the `context-repository` project so it matches this same model.
- Keep novelty and maintenance structures subordinate to current-state working
  context rather than letting them dominate it.

## Constraints

- The supervisor still must not edit project code directly.
- Current-state files should stay small, overwrite-friendly, and easy to diff.
- Logs and derived queues may inform the control plane, but should not pollute
  the files loaded as working context.
- This repo should model the desired context-repository design for the rest of
  the workspace: current state first, reference layers second, raw logs
  elsewhere.
