# ADR-0001: Supervisor context-repo created

Date: 2026-04-14
Status: accepted

## Context

The workspace already runs an automated self-reflection loop (per-project
reflections every 12h, cross-cutting synthesis ~1h later, nightly
server-health + maintenance + weekly schedule). Session state was supervised
by systemd. The accumulated outputs live in `/opt/projects/.meta/`.

What was missing: a durable, curated substrate for the *supervisor* itself —
the agent powering the `general` tmux session and the nightly scheduled jobs.
State was scattered across CLAUDE.md, `.meta/`, `.handoff/`, `.plans/`, and
in-session Claude JSONL transcripts.

Symptoms:

- Every supervisor session re-derived the same architectural rationale
- No clean handoff mechanism between supervisor instances over time
- The supervisor role was not distinct from "just another Claude session" —
  specifically, the governance contract's control-plane/execution-plane split
  had no enforcement at the supervisor layer
- No path for Codex to serve as supervisor interchangeably with Claude

## Decision

Create `/opt/projects/supervisor/` as a git-initialized context-repo with:

- Canonical agent charter in `AGENT.md` (symlinked from `CLAUDE.md` and `AGENTS.md` for harness-native discovery)
- `decisions/` — ADR-style append-only architectural records
- `handoffs/INBOX/` and `handoffs/ARCHIVE/` — inter-instance handoff channel
- `events/` — append-only event log for supervisor actions
- `skills/` — shared, agent-agnostic capabilities
- `playbooks/` — step-by-step runbooks for recurring supervisor tasks

The repo is agent-agnostic: both Claude and Codex read the same AGENT.md.
Harness-specific conventions are handled via symlinks, not by duplicating
content.

## Consequences

**Enables:**

- Supervisor can run under either Claude or Codex with parity
- Durable state survives session restarts and crosses between agent harnesses
- Decisions and playbooks can be reviewed, linted, and versioned like code
- The pattern becomes a template for per-project manager agents (the
  "project-PM" layer is the same shape, one level down)

**Forecloses / costs:**

- One more repo to maintain. Not free — must prune handoffs and review ADRs.
- Risk of the supervisor repo becoming a dumping ground if the
  `.meta/` → `supervisor/` promotion discipline isn't held.
- Skills registered via symlinks into `~/.claude/skills/` and `~/.codex/skills/`
  add a filesystem coupling that a harness update could break. Playbook
  `install-skills.md` documents the install/uninstall.

## Alternatives considered

1. **Keep everything in `.meta/`**. Rejected: `.meta/` is
   auto-generated and pruned. Conflating durable and ephemeral state there
   erodes both.

2. **Promote the existing `context-repository/` to host supervisor content**.
   Rejected: `context-repository/` charter is explicit — pure-Markdown spec
   layer, no operational state. Adding supervisor-instance state (handoffs,
   event logs) would violate its charter.

3. **Put supervisor state inside `/opt/projects/CLAUDE.md` and rely on
   auto-memory**. Rejected: CLAUDE.md is already overloaded; auto-memory at
   `/root/.claude/projects/-opt-projects/memory/` is Claude-specific and
   invisible to Codex.

4. **Defer until the feature-session/hierarchy work is done**. Rejected: the
   supervisor repo is a prerequisite for per-project PM agents. Doing this
   first sets the pattern.
