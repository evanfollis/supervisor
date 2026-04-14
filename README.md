# supervisor

Context-repository for the workspace supervisor agent — the reasoning substrate
for system-wide management of `/opt/projects/`.

This repo is **not** a project and **not** product code. It is the durable
substrate for the session(s) that orchestrate everything else on this server:
the `general` tmux session, nightly maintenance jobs, cross-cutting synthesis,
and any future project-manager agents that inherit this pattern.

## Role

The supervisor agent is the one that:

- Reads the outputs of `workspace-reflect` and `workspace-synthesize`
- Coordinates work across project sessions
- Writes and reads inter-instance handoffs (between itself over time)
- Owns workspace-level architecture decisions
- Delegates feature work to project sessions

It is **not** the agent that writes project code. Project sessions (atlas,
command, mentor, etc.) do that. The supervisor runs above them.

## Agent-agnostic

The supervisor can be run by either Claude Code or Codex. Both read the same
canonical instructions from `AGENT.md`. `CLAUDE.md` and `AGENTS.md` are
symlinks to `AGENT.md` so each agent's native discovery convention resolves
to the same content. Skills and playbooks are written in a way that doesn't
assume which harness is executing them.

This also makes the repo a **test-bed** for per-project manager agents: if the
structure works here, it's what every project's supervisor-of-its-subagents
will look like.

## Structure

| Path | Purpose |
|---|---|
| `AGENT.md` | Canonical system prompt / charter for the supervisor agent |
| `docs/` | Durable architecture + operating notes |
| `decisions/` | ADR-style append-only decision records (one file per decision) |
| `handoffs/INBOX/` | New handoffs between supervisor instances — read at session start |
| `handoffs/ARCHIVE/` | Processed handoffs kept for history |
| `skills/` | Shared skills (agent-agnostic recipes) |
| `playbooks/` | Step-by-step runbooks for recurring supervisor tasks |
| `events/` | Append-only event log of supervisor actions |

## Reentry

On session start, the supervisor reads, in order:

1. `AGENT.md` — charter
2. `handoffs/INBOX/` — anything the previous instance left
3. `/opt/projects/.meta/LATEST_SYNTHESIS` → latest cross-cutting file
4. `/opt/projects/.health-status.txt` → server health one-liner
5. `decisions/` recent entries — durable architectural context

On session exit (or at end of any meaningful work block), the supervisor writes
a short handoff under `handoffs/INBOX/<iso>-<topic>.md` summarizing state worth
preserving.

## What lives here vs. `/opt/projects/.meta/`

- `.meta/` — ephemeral, auto-generated (reflections, syntheses, host snapshots). Pruned on a schedule.
- `supervisor/` — durable, human-curated-or-reviewed. Decisions, playbooks, skills, agent charter. Git-tracked.

If you find yourself writing the same ad-hoc procedure into `.meta/` twice,
promote it to `supervisor/playbooks/`. If you find yourself re-deriving the
same architectural rationale, promote it to `supervisor/decisions/`.
