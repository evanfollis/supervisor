# ADR-0009: session_id commit trailers for state-change provenance

Date: 2026-04-14
Status: proposed

## Context

The context-repository mental model defines three retrieval modes:

1. **What is true now?** → read the context repo.
2. **What changed?** → read `git diff` / commit history.
3. **Why did it change?** → follow the commit's `session_id` into the
   transcript / log store.

The supervisor repo implements (1) and (2) but not (3). Recent commits (e.g.
`02977d0`, `1abdf05`) carry no pointer back to the session transcript that
produced them, so a future reader cannot walk from a state change to the
rationale without guessing which JSONL covers the timestamp. This weakens
every downstream mechanism that is supposed to compound meta observations
(reflections, syntheses, policy compression).

The same gap exists project-side and will limit reflection quality there too,
but the supervisor repo is the correct place to model the convention before
proposing it outward.

## Decision

Every supervisor-repo commit includes a `session_id` trailer in the commit
message identifying the session transcript responsible for the change:

```
<subject line>

<optional body>

session_id: <transcript-basename>
agent: claude|codex
```

Rules:

- **`session_id`** is the basename of the current session's JSONL transcript
  (for Claude: the file under `/root/.claude/projects/-opt-workspace-supervisor/`
  active for this session; for Codex: the equivalent under
  `/root/.codex/sessions/**/` with cwd `/opt/workspace/supervisor`). If the
  session is not transcript-backed (e.g. a scheduled job with its own log),
  use that log's filename.
- **`agent`** is the runtime that produced the commit.
- Commits made by humans directly (not through an agent session) omit the
  trailer; absence is a valid signal that the change was human-authored.
- Scheduled maintenance jobs that commit to this repo include a trailer
  pointing at their job-run artifact under `/opt/workspace/runtime/.meta/`.

Enforcement:

- Add a `commit-msg` hook under `supervisor/scripts/` that injects the trailer
  when run by an agent session and an environment variable
  (`SUPERVISOR_SESSION_ID`, `SUPERVISOR_AGENT`) is present.
- Agent sessions export those variables at startup. The variables are set by
  the systemd unit / tmux wrapper, not by the agent itself, so the trailer
  cannot be forged by a misbehaving agent without cooperation from the
  supervisor launcher.
- The hook is advisory, not blocking: if the variables are absent, the commit
  proceeds without a trailer (preserving human-author behavior).

## Consequences

### Positive

- Retrieval mode (3) becomes mechanical: `git show <sha>` exposes the
  transcript pointer directly.
- Reflection and synthesis jobs can link state changes to the reasoning that
  produced them without timestamp heuristics.
- The convention is cheap to adopt in project repos later; this ADR models it
  in a low-risk surface first.

### Costs

- Commits gain two trailer lines. Acceptable.
- The launcher must set `SUPERVISOR_SESSION_ID` / `SUPERVISOR_AGENT` reliably
  before the agent starts, otherwise trailers silently disappear. This is a
  substrate responsibility and should be covered by a follow-up to
  `scripts/lib/session-supervisor.sh`.
- Human-authored commits look different from agent-authored commits. This is
  intentional — the shape of the commit already reveals authorship, and
  pretending otherwise would hide a load-bearing distinction.

## Alternatives considered

1. **Put session_id in the commit body prose.** Rejected: trailers are
   machine-parseable; prose is not.
2. **Store the mapping out-of-band (e.g. a sidecar file).** Rejected:
   duplicates git's own storage and introduces a new sync problem. Commits
   already carry author, timestamp, and message — session_id belongs there.
3. **Require the trailer (block commits without it).** Rejected: would block
   legitimate human commits and emergency manual fixes.
4. **Scope the convention workspace-wide in this ADR.** Rejected: the
   supervisor repo is the right pilot. Promote to `/opt/workspace/CLAUDE.md`
   after the hook has run here for a few weeks.
