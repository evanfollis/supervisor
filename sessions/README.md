# Sessions

Runtime metadata for active feature sessions. One JSON file per feature session.

## Purpose

The supervisor repo is the canonical state surface for workspace orchestration.
Persistent project sessions are declared in
`/opt/projects/scripts/lib/sessions.conf`. Ephemeral **feature sessions** — the
third tier below general and per-project — are tracked here.

## File shape

`<project>--<slug>.json`:

```json
{
  "project": "mentor",
  "slug": "kalman-filter",
  "tmux_name": "mentor--kalman-filter",
  "branch": "feat/kalman-filter",
  "base_branch": "main",
  "worktree": "/opt/projects/.features/mentor/kalman-filter",
  "agent": "claude",
  "created_at": "2026-04-14T15:30:00Z",
  "parent_session": "mentor"
}
```

## Rules

- **One file per session.** Written by `ws feature`, removed by `ws close`.
- **Gitignored.** Runtime state, not durable decisions. If a record matters
  beyond the session's life, promote it to a handoff or ADR.
- **Authoritative for `ws tree`.** Don't maintain a parallel index.
- **Don't edit by hand.** If metadata is wrong, close the session and reopen.

See `decisions/0002-feature-sessions.md` for the design rationale.
