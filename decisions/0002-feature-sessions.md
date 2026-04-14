# ADR-0002: Feature sessions — always-worktree, agent-selectable

Date: 2026-04-14
Status: accepted

## Context

The workspace has long-lived project sessions (one tmux session per project,
systemd-supervised). Users want a third tier below project: short-lived
**feature sessions** for focused work — a feature branch, a bug investigation,
an exploratory chat — without polluting the project session's conversation or
stepping on the project's checkout.

Two axes that looked like UX knobs, and why they aren't:

1. **Branch-scoped vs exploratory.** User's stated requirement: "seamless way
   to handle both... without too many knobs/dials." If creation forks on
   `--branch`, every caller has to decide up-front whether their chat will
   produce code. That decision is premature — exploration routinely turns into
   a branch. Fork the creation path and you force the user to rename, recreate,
   or live with a mismatch.

2. **Claude vs Codex.** Unlike the above, this *is* a real choice the user
   makes deliberately — some work is better suited to one harness. A flag
   here is appropriate.

## Decision

### Always create a worktree + branch

`ws feature <slug>` always:

1. Creates a git worktree at `/opt/projects/.features/<project>/<slug>/`
2. Creates a branch `feat/<slug>` (from the project's default branch)
3. Starts a tmux session `<project>--<slug>` cwd'd into the worktree
4. Writes metadata to `/opt/projects/supervisor/sessions/<project>--<slug>.json`

No `--branch` flag. No "exploratory mode." Worktrees are cheap (shared `.git`,
no extra checkout cost beyond working-tree files), and branch creation is free.
If the session produces no work, `ws close` detects the empty branch and
removes it silently. If it produces work, close handles it.

### Tmux session naming: `<project>--<slug>`

Tmux target syntax uses `.` as the `session.pane` separator and `:` as
`session:window`. Using either in a session name creates ambiguity in
`tmux send-keys -t <target>`. `--` is unambiguous and matches the feature-
branch feel.

### Agent selection via `--agent claude|codex`

Default: `claude`. Flag is explicit and recorded in metadata so `ws tree`,
reflection, and close logic can route appropriately.

### Metadata lives in the supervisor repo, not in the worktree

`/opt/projects/supervisor/sessions/<name>.json`:

```json
{
  "project": "mentor",
  "slug": "kalman-filter",
  "branch": "feat/kalman-filter",
  "worktree": "/opt/projects/.features/mentor/kalman-filter",
  "agent": "claude",
  "created_at": "2026-04-14T15:30:00Z",
  "parent_session": "mentor"
}
```

The supervisor repo is the canonical state surface for workspace orchestration.
Keeping metadata there (instead of inside each worktree) means:

- One place for `ws tree` to read
- Worktrees stay clean of meta pollution
- State survives worktree deletion (history of closed features if we ever want it)

The `sessions/` directory is gitignored — this is runtime state, not decisions.

### Not systemd-supervised

Feature sessions are ephemeral. If one crashes, that's signal, not something to
paper over with automatic restart. Only the 7 persistent sessions
(general + 6 projects) get systemd supervision.

### Close logic (`ws close <name>`)

Uniform path, no exploratory/feature fork:

1. Kill tmux session.
2. Check worktree state:
   - **Empty** (no commits, no uncommitted changes): remove worktree + branch silently.
   - **Uncommitted changes**: prompt — stash, commit, or abort.
   - **Committed, branch merged**: remove worktree + branch.
   - **Committed, branch unmerged**: prompt — push, keep, or discard.
3. Remove metadata file.

## Consequences

**Enables:**

- Uniform creation and close flow — one code path, no knob-driven branches.
- `ws tree` can render the full hierarchy (general → project → feature) from
  `sessions.conf` + `supervisor/sessions/*.json`.
- Features are portable: a Claude feature session can be "handed off" to Codex
  by closing and reopening with `--agent codex` against the same branch
  (future work).

**Forecloses / costs:**

- Users who truly want no-branch exploration now have a small branch to
  clean up. Acceptable — close handles it silently.
- Worktree count scales with active feature sessions. Negligible — each worktree
  is a few MB of working-tree files.
- Cross-worktree file edits (edit project from inside feature cwd) are
  possible and dangerous. Mitigated by: feature sessions should work in their
  own cwd; if they need to change the project itself, that's a project-session
  task.

## Alternatives considered

1. **`--branch` flag to split creation.** Rejected per user UX requirement.
2. **Metadata inside each worktree** (`.ws/meta.json`). Rejected: pollutes
   the worktree, lost on worktree removal, no central index.
3. **Supervise feature sessions with systemd.** Rejected: ephemerality is a
   feature. Auto-restarting a crashed feature chat hides the signal.
4. **Session name uses `:` or `.`.** Rejected: tmux target-syntax ambiguity.
