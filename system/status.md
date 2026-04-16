# System Status

## Role

This supervisor repo is the workspace control plane. Its working context should
represent the best current understanding of the system, not a log of
interactions.

## Current operating model

- Executive work launches from `/opt/workspace`, not from a project repo.
- `/opt/workspace/supervisor/` is the durable governance repo and current-state
  bundle.
- `/opt/workspace/runtime/` holds generated state, telemetry, handoffs, and
  other operational artifacts.
- The principal-facing top layer is now `executive`; it normally carries the
  `supervisor` posture and carries the `operator` posture only when capability
  attestation proves host-control access.
- `system/`, `projects/`, and `roles/` are the primary working-context
  surfaces.
- `projects/*.md` is the standing per-project shaping surface: the executive's
  running status across governed projects should be visible there rather than
  reconstructed from transcript memory.
- `decisions/`, `docs/`, `playbooks/`, `skills/`, and `ideas/` are reference
  layers and promotion targets.
- `git history` is the state-transition log for this repo.
- `session_id=<id>` in commit messages is the intended provenance bridge from
  context-repo state changes to transcript rationale.
- `workspace.sh context` is the preferred way to load the canonical current
  context bundle in one pass.

## Active focus

- Keep the supervisor substrate current-state-first and resist drift back
  toward archive-heavy working context.
- Make the executive surface honest about capability: top-level authority is
  real only when attested, not because the session is named `general`.
- Correct the `context-repository` project so it matches this same model.
- Keep novelty and maintenance structures subordinate to current-state working
  context rather than letting them dominate it.
- Improve PM-layer autonomy so repeated supervisor nudges become policy,
  workflow, or expectation changes instead of permanent manual oversight.
- Treat friction capture plus policy refinement as the main mechanism for
  moving the whole stack up, analogous to a policy-search loop.
- Push `command` toward a true executive control-plane product, not a better
  looking collection of session and terminal utilities.

## Constraints

- The supervisor still must not edit project code directly.
- Current-state files should stay small, overwrite-friendly, and easy to diff.
- Logs and derived queues may inform the control plane, but should not pollute
  the files loaded as working context.
- This repo should model the desired context-repository design for the rest of
  the workspace: current state first, reference layers second, raw logs
  elsewhere.
