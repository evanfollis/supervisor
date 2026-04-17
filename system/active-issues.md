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
- **Watch for second-signal drift**: if the redesign proposal comes back
  oriented around new abstract schemas, that's the same failure class
  repeating and warrants escalation.

### Interaction-derived signal triage

- The system can now capture and prioritize novelty, but it still lacks a
  deterministic signal taxonomy for noise, local friction, policy candidates,
  and compoundable value.
- Active control-plane item: `IDEA-0002`.

### `/review` enforcement gate → live; Command blocks on git

- `scripts/lib/preflight-deploy.sh` now fails deploys lacking review
  artifacts for code-touching commits (supervisor commit `668c7b0`,
  cross-cutting-2026-04-14 Proposal 1).
- `command` has no git repo, so the gate is silently permissive for the
  one project most obviously designed to catch. Delegated:
  `/opt/workspace/runtime/.handoff/command-bootstrap-git.md`. Until that
  returns, treat command as an exemption that must be closed, not a
  baseline.

### Telemetry schema gap

- `events.jsonl` has no required-fields contract. Command floods
  `sessions.listed`; atlas emits nothing. Meta-scan produces false
  positives because it can't distinguish smoke vs. real traffic.
- **S1-P2 implemented but not deployed**: command tick eb18e35 added `sourceType` as
  required field to `TelemetryEvent` with all 16 call sites updated; build clean, pushed
  to GitHub. Runtime still serving pre-change binary — `sourceType` will appear in events
  only after next deploy. Disposition: `accepted-not-fully-verified` (code verified, runtime not).
- Telemetry rotation: command shipped `scripts/rotate-telemetry.sh` (eb18e35) as a
  project-specific script. A shared workspace-level rotation primitive + systemd timer
  (`supervisor/scripts/lib/telemetry-rotate.sh`) is still needed (S4-P3 from synthesis).

### Command is still too close to its mechanism

- `command.synaplex.ai` is now the live executive front door for capability
  attestation, ensuring `executive-codex`, and recovering session fabric.
- But the product still leaks too much implementation detail. Recent work
  exposed that `Sessions` and `Orchestrate` had divergent Codex models and the
  system drifted toward local UI cleanup before fully repairing the underlying
  control-plane abstraction.
- The active pressure is no longer "make command prettier." It is "make
  command a trustworthy executive control plane that reduces principal
  supervision burden."
- Immediate live failure: the homepage executive surface still says the message
  was sent, but does not return a real conversational response. The principal
  is still being pushed down into dead lane/session reasoning.
- Active PM task:
  `/opt/workspace/runtime/.handoff/command-fix-broken-executive-conversation-2026-04-15T19-28Z.md`
- Current state: the `command` lane has implemented the direct-response fix on
  disk and validation passes. The remaining blocker is operational deployment
  of the updated service.
- See friction record: `/opt/workspace/supervisor/friction/FR-0016-command-still-behaves-like-ui-over-sessions.md`

### Executive relapsed into implementation instead of shaping the `command` PM

- The principal correctly called out that the executive was still trying to be
  a do-it-all surface instead of operating at the PM-shaping level.
- This was not just a tone issue. Workspace-root executive sessions directly
  touched `command` repeatedly while the real need was clearer PM pressure,
  product architecture, and acceptance criteria for the browser control plane.
- Immediate correction: treat `command` as a PM/product-system problem and hold
  the next pass there, rather than continuing to patch it from the executive
  lane.
- See friction record:
  `/opt/workspace/supervisor/friction/FR-0018-executive-relapsed-into-project-implementation.md`

### Synthesis proposals pending attended action (cross-cutting-2026-04-16T15-25-24Z)

Reviewed in tick 2026-04-17T02-49Z. All require scripts/lib or hook changes (Tier C).

- **S5-P1 — Dispositions verified field**: schema change on `dispositions.jsonl` + reflect/synthesize prompt update. Dispositions need separate `verified` / `verified_evidence` fields so `accepted-not-verified` items continue to surface. Requires attended session to update reflect/synthesize prompts in `scripts/lib/`.
- **S5-P2 — ADR acceptance gate**: pre-commit hook on supervisor repo blocking `status: accepted` without a review artifact. Requires scripts/lib edit (Tier C). Highest urgency — 3 ADRs already bypassed.
- **S5-P3 — Shared telemetry rotation primitive**: workspace-level `scripts/lib/telemetry-rotate.sh` + systemd timer (separate from command's project-specific script). S4-P3 partially addressed by command tick; shared primitive still missing.
- **S5-P5 — Disposition stalled event**: if `verified:false` >2 reflection cycles after acceptance, emit `disposition_stalled` + URGENT handoff to owner. Requires supervisor-tick.sh amendment.
- **S5-P4 — CLAUDE.md carry-forward escalation**: DONE — landed in bd5a854.

## Structural (supervisor self-alignment)

These items concern the supervisor repo matching its own current-state
model. Resolved items are removed; remaining items are tracked to an ADR.

- **Events live inside the repo.** Charter §Event model locates
  `events/supervisor-events.jsonl` in-repo. Should be in
  `/opt/workspace/runtime/.telemetry/` with a pointer here. Addressed
  by **ADR-0012 (accepted)**; migration queued as a separate execution
  task.
- **`handoffs/ARCHIVE/` is a log.** Resolution is already in git.
  Addressed by **ADR-0012 (accepted)**; migration queued with events.
- **`AGENT.md` duplicates `system/status.md`** on reentry order and
  operating model. Two sources of truth for "how the supervisor operates"
  will drift. **Open — needs ADR or direct compression.** Candidate for
  next pass.
- **Idea JSON carries inline `history[]` log.** Per-file append state
  duplicates git and events. Strip history; rely on `git log -- ideas/…`
  and `idea_*` events. **Open — touches `scripts/lib/idea-ledger.py`.**
- **Supervisor pressure was implicit, not surfaced.** `pressure-queue.md`
  now exists to make dropped pressure visible. The discipline still needs to
  prove itself in live use.

## Structural (workspace-wide)

### Current-state bundle discipline must hold

- `workspace.sh context` now emits the canonical current-state bundle.
- Reentry should continue to prefer `system/status.md`,
  `system/active-issues.md`, `system/active-ideas.md`, and relevant
  `projects/` / `roles/` state files.
- Reference and archive layers should be opened only when the state
  surfaces point at them.

### Cross-agent project transport is still soft

- Runtime handoffs exist and are the intended project-session routing
  surface.
- Direct opposite-agent CLI invocation from the supervisor is unreliable
  in the current sandbox: local `claude -p` calls hang without returning
  usable output.
- The control plane should not assume that ad hoc CLI invocation is a
  reliable substitute for a proper session-to-session transport and
  acknowledgment path.

## Resolved (removed from this surface; see git history for detail)

Previously-listed items that have been closed:

- *reflect-all.sh stdin bug* (2026-04-15) — fixed in commit 6c91398 by
  redirecting the `reflect.sh` subprocess's stdin from `/dev/null`. Next
  12h reflection cycle (14:17 UTC) will validate all 7 projects produce
  artifacts. Source: FR (pending), synthesis 2026-04-15T03:26 Pattern #1.
- *workspace.sh doctor broken* (2026-04-15) — fixed in commit 6c91398:
  resolve `$0` with `readlink -f` so invocation via the
  `/opt/workspace/workspace.sh` symlink finds the real `scripts/lib/`.
  FR-0008.
- *Server patch + reboot overdue* (2026-04-15) — 45 upgradable packages
  applied, kernel 6.8.0-107 installed; reboot executed same session.
  FR-0009.
- *Supervisor tick paused by hold file* (2026-04-15) — resolved in attended
  session by removing `/opt/workspace/runtime/.locks/supervisor-tick.hold`.
- *Post-reboot runtime health surfaces stale* (2026-04-15) — resolved in
  attended session; latest snapshot is
  `/opt/workspace/runtime/.meta/server-health-2026-04-15T12-57-45Z.md`.
- *session_id in commit trailers* — ADR-0009 accepted; all supervisor
  commits from 2026-04-14 onward carry the trailer.
- *`docs/` promotion/retirement rule* — `docs/README.md` already
  defines it.
- *`projects/` retention rule* — `projects/README.md` already defines
  it.
- *`sessions/` retention rule* — `sessions/README.md` already defines it.
