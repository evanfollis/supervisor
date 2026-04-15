# Active Issues

## Immediate

### Context repository mismatch

- The `context-repository` project is currently chartered as an abstract spec
  layer with no operational state.
- Intended design is the opposite: current compressed state in-repo, logs and
  transcripts elsewhere, git history as the state-change narrative.
- A first opposite-agent redesign attempt drifted further toward canonical
  schemas and abstract governance docs instead of implementing current-state
  context surfaces.
- Active control-plane item: `IDEA-0003`.
- Routed via handoff: `/opt/workspace/runtime/.handoff/context-repo-context-repo-redesign.md`

### Interaction-derived signal triage

- The system can now capture and prioritize novelty, but it still lacks a
  deterministic signal taxonomy for noise, local friction, policy candidates,
  and compoundable value.
- Active control-plane item: `IDEA-0002`.

### Supervisor repo self-alignment with current-state model

The supervisor repo partially embodies the intended context-repo model but
still carries log-shaped and reference-shaped surfaces that dilute the
working-context bundle. Items marked *(ADR required)* contradict the current
charter and must be routed through a decision before being changed.

- **Events live inside the repo.** `events/supervisor-events.jsonl` is
  append-only telemetry and should sit under `/opt/workspace/runtime/.telemetry/`
  with only a pointer in `system/`. *(ADR required — charter §Event model
  currently locates the log here.)*
- **Idea JSON carries an inline `history[]` log.** Per-file append state
  duplicates git and events. Strip history; rely on `git log -- ideas/…` and
  `idea_*` events.
- **`handoffs/ARCHIVE/` is a log.** Resolution is already in git. Either
  relocate to runtime or drop. *(ADR required — charter §Reentry step 3
  specifies archive path.)*
- **No `session_id` in commit messages.** The "why did it change" retrieval
  path from the context-repo model is not wired up. Tracked as ADR-0009.
- **`docs/` has no promotion/retirement rule.** Files such as
  `workspace-migration-plan.md` look like completed work still loaded as live
  reference. Add a `docs/README.md` retention rule.
- **AGENT.md duplicates `system/status.md`** on reentry order and operating
  model. Two sources of truth for "how the supervisor operates" will drift.
  Compress AGENT.md to charter-only; keep operating model in `system/`.
- **`projects/` retention rule is implicit.** State it: one file per project
  currently under supervisor attention; absence means project-session
  responsibility.
- **`sessions/` has no retention rule.** Add: closed feature sessions delete
  their state file; lineage lives in git + `feature_closed` events.

## Structural

### Current-state bundle discipline must hold

- `workspace.sh context` now emits the canonical current-state bundle.
- Reentry should continue to prefer `system/status.md`,
  `system/active-issues.md`, `system/active-ideas.md`, and relevant
  `projects/` / `roles/` state files.
- Reference and archive layers should be opened only when the state surfaces
  point at them.

### Cross-agent project transport is still soft

- Runtime handoffs exist and are the intended project-session routing surface.
- Direct opposite-agent CLI invocation from the supervisor is unreliable in the
  current sandbox: local `claude -p` calls hang without returning usable output.
- The control plane should not assume that ad hoc CLI invocation is a reliable
  substitute for a proper session-to-session transport and acknowledgment path.
