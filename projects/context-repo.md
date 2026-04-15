# Project: context-repo

## Current status

- The project is active because its current charter is misaligned with intended
  system design.
- It currently presents itself as an abstract specification layer with no
  operational state.
- The first Claude-side redesign attempt reinforced that framing by expanding
  canonical spec/governance documents rather than introducing state surfaces.
- The target model is a state-oriented context repository with small current
  files, logs elsewhere, and provenance through `session_id` commit messages.

## What needs to change

- Reframe the repo around current-state surfaces such as:
  - `system/status.md`
  - `system/active_issues.md`
  - `system/active_ideas.md`
  - `projects/<slug>/status.md`
  - `roles/*.md`
- Relegate specs and abstract schemas to a subordinate reference layer.
- Define what belongs in repo state vs DB/log/transcript layers.
- Rewrite the repo charter so these state files become the primary operating
  surface and the abstract substrate becomes reference material.

## Active artifact links

- Supervisor idea: `/opt/workspace/supervisor/ideas/IDEA-0003-redesign-context-repository-around-current-state-context-surfaces.json`
- Handoff: `/opt/workspace/runtime/.handoff/context-repo-context-repo-redesign.md`
