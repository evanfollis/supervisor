---
name: System Status
description: Current operating model and active focus for the supervisor control plane
type: front-door
updated: 2026-07-12
---

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

## System topology (ADR-0027; supersedes ADR-0023)

- **synaplex.ai is the system**: methodology, lab, knowledge projection,
  public surface, and operator surface.
- **atlas** and **skillfoundry** are domain pods that both contribute and
  consume system knowledge.
- **context-repository** owns the formal canon obligations and schemas; it is
  not the knowledge system or a runtime memory product.
- **command** is Synaplex's operator surface.
- Per ADR-0044, the first derived knowledge projection belongs under
  `projects/synaplex/knowledge/`; it remains subordinate to canon Decisions.
- Per ADR-0046, `synaplex.ai` is the static public-safe knowledge projection;
  `command.synaplex.ai` is the authenticated owner projection over the same
  contract with private operational overlays.

Personal projects (`mentor`, `recruiter`) were removed from this server
2026-04-18. They remain in GitHub as personal side projects and do not
consume workspace attention.

## Active focus

- Keep the supervisor substrate current-state-first and resist drift back
  toward archive-heavy working context.
- Make the executive surface honest about capability: top-level authority is
  real only when attested, not because the session is named `general`.
- Keep novelty and maintenance structures subordinate to current-state working
  context rather than letting them dominate it.
- Improve PM-layer autonomy so repeated supervisor nudges become policy,
  workflow, or expectation changes instead of permanent manual oversight.
- Treat friction capture plus policy refinement as the main mechanism for
  moving the whole stack up, analogous to a policy-search loop.
- The reflect loop ran clean for the current 2026-07-12 cycle; no supervisor
  status intervention is needed.
- Restore Command's atomic deployment boundary, then refocus it as the owner
  dashboard: decisions, anomalies, loop health, evaluation/model telemetry,
  and private operational pressure first; session/terminal tools second.
- Make `synaplex.ai` the human- and agent-addressable public projection of live
  accepted knowledge, derived research artifacts, and cited expert insight.
- Make the first full knowledge cycle the dominant cross-project priority:
  Claim → Evidence → Decision → invariant → projection → pod consumption →
  reflection. Do not expand topology ahead of this proof.
- Retain full-fidelity transcripts, telemetry, reflections, and syntheses while
  keeping only bounded indexes and recent artifacts on the hot execution path
  (ADR-0043).
- Support `atlas` through its epistemic-build phase toward the systematic
  trading threshold. This is the primary commercial compounding path.
- Support `skillfoundry` through Stage-1 external-evidence accumulation.
  Agentic inbound is the current primary channel.

## Constraints

- The supervisor still must not edit project code directly.
- Current-state files should stay small, overwrite-friendly, and easy to diff.
- Logs and derived queues may inform the control plane, but should not pollute
  the files loaded as working context.
- This repo should model the desired context-repository design for the rest of
  the workspace: current state first, reference layers second, raw logs
  elsewhere.
