# ADR-0004: Recursive delegation stack and transcript-governed oversight

Date: 2026-04-14
Status: accepted

## Context

The workspace already has the beginnings of a governance stack:

- persistent project sessions supervised by systemd
- a durable supervisor repo for the `general` session
- scheduled reflections and cross-project synthesis
- append-only workspace telemetry and handoff channels

What was still missing was load-bearing enforcement around role identity and
visibility:

- A session started at `/opt/workspace` could behave like a project worker,
  a supervisor, or an ad hoc explorer. The intended role was implied, not
  enforced.
- The supervisor had durable access to project repos and session artifacts,
  but no normalized, always-on view of direct human interaction with lower
  layers.
- Governance boundaries remained mostly prompt-level norms. If the "easy,
  softer way" was to bypass the supervisor and talk directly to a project
  session, the control plane had no guaranteed post-hoc trace of that
  intervention.

The user requirement is explicit: the meta layer should be the default point of
contact, should survive routine bypasses without losing awareness, and should
be simple enough that operators do not need to remember a brittle workflow.

## Decision

Adopt the **Recursive Delegation Stack** as the canonical workspace governance
model and back it with three concrete control-plane mechanisms.

### 1. Name the stack explicitly

The workspace operates as four governance layers:

1. project agents
2. project-manager agents
3. workspace supervisor / meta agent
4. human principal

Escalation rises. Policy descends.

### 2. Make session role identity explicit

Persistent sessions in `scripts/lib/sessions.conf` now declare an explicit role.
At minimum, the workspace distinguishes:

- `supervisor`
- `project`

The workspace root (`/opt/workspace`) is treated as a supervisor surface by
default, not as a neutral scratch directory.

### 3. Add transcript-governed oversight

The control plane now normalizes agent transcript traffic into an append-only
session trace under `runtime/.telemetry/session-trace.jsonl`, driven by an
always-on systemd timer. The scanner consumes durable transcript artifacts
directly from Claude and Codex storage, so visibility does not depend on users
or agents voluntarily reporting what happened.

The normalized session trace is an index, not the canonical transcript. The
source transcript files remain the ground truth.

## Consequences

### Positive

- The meta layer now has a default embodiment and a default surface.
- Direct human intervention in project or feature sessions becomes visible to
  the control plane without requiring behavioral compliance from lower layers.
- Cross-agent oversight becomes harness-agnostic: Claude and Codex are both
  scanned from their durable transcript surfaces.
- Governance becomes simpler to follow operationally: attach at the workspace
  root for the supervisor; attach inside repos for project work.

### Costs

- Transcript normalization adds another always-on control-plane job to keep
  healthy.
- The transcript trace is intentionally derivative, which means two surfaces
  must be kept conceptually distinct: source transcripts vs normalized index.
- Session identity is still partly soft. A sufficiently privileged human can
  always open an arbitrary ad hoc session. The system response is to make that
  action visible and governable, not to pretend it can never happen.

## Alternatives considered

1. **Rely on prompts alone.**
   Rejected: too easy to bypass and too hard to audit.

2. **Require all work to flow through the supervisor session.**
   Rejected: too brittle under real runtime pressure. The system should remain
   governable even when humans intervene directly elsewhere.

3. **Scrape live tmux panes as the source of truth.**
   Rejected: pane scraping is lossy and terminal-dependent. Durable transcript
   stores are the correct substrate.

4. **Enforce boundaries with OS-level user separation immediately.**
   Deferred: stronger in principle, but a larger operational change than the
   workspace needs today. Transcript-governed oversight and explicit role
   identity are lower-friction first steps.
