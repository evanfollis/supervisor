# Playbook: Feature session lifecycle

**Trigger**: user (or supervisor on behalf of user) wants a scoped chat session
for a feature branch, bug investigation, or exploratory thread, separate from
the project's main session.

**Owner**: supervisor

**Preconditions**:
- Target project is in `/opt/projects/scripts/lib/sessions.conf`
- Project working tree is clean (worktree base will be the project's default branch)
- `jq` installed, `tmux` running, systemd workspace-session services healthy

**Outputs**:
- Worktree at `/opt/projects/.features/<project>/<slug>/`
- Branch `feat/<slug>` tracking the project's default branch
- Tmux session `<project>--<slug>` running the chosen agent
- Metadata file `/opt/projects/supervisor/sessions/<project>--<slug>.json`
- Event `feature_opened` appended to `supervisor/events/supervisor-events.jsonl`

## Steps

1. **Open the session.**
   ```
   ws feature <slug> [--project <name>] [--agent claude|codex]
   ```
   - Slug: lowercase, alphanumeric + hyphens.
   - Project defaults to the project inferred from `$PWD`; pass `--project`
     when running from outside a project dir (e.g. from `general`).
   - Agent defaults to `claude`.

   **Verify**: `ws tree` shows the new feature under its project with status
   `(up)`. Metadata file exists at
   `/opt/projects/supervisor/sessions/<project>--<slug>.json`.

2. **Attach and work.**
   ```
   ws-attach <project>--<slug>
   ```
   Session cwd is the worktree. All commits happen on `feat/<slug>`.

   **Verify**: `git -C <worktree> rev-parse --abbrev-ref HEAD` returns
   `feat/<slug>`.

3. **Integrate (from the parent project session, not the feature).**
   When work is ready to merge, open a PR from `feat/<slug>` or fast-forward
   merge from the project session:
   ```
   git -C <project-dir> merge --ff-only feat/<slug>
   git -C <project-dir> push
   ```

   **Verify**: `git -C <project-dir> merge-base --is-ancestor feat/<slug> <base>`
   exits 0.

4. **Close the session.**
   ```
   ws close <project>--<slug>
   ```
   Behavior by worktree state:
   - **Empty** (no commits, no uncommitted changes): silent cleanup.
   - **Uncommitted changes**: refuses unless `--force`. Commit inside the
     worktree first.
   - **Branch merged**: cleans up worktree + branch + metadata.
   - **Branch unmerged with commits**: refuses unless `--force`. Push and PR
     first; `--force` keeps the branch and removes only the worktree + meta.

   **Verify**: `ws tree` no longer lists the feature; `ls
   /opt/projects/.features/<project>/` does not contain the slug.

## Rollback

- If worktree add succeeded but tmux-session launch failed: remove worktree
  manually (`git -C <project-dir> worktree remove <path> --force`; delete
  metadata file). The ws feature command is idempotent — you can safely rerun
  after cleanup.
- If `ws close` is interrupted mid-cleanup: rerun it. It tolerates missing
  tmux session, missing worktree, or missing branch.

## Notes

- Feature sessions are **not** systemd-supervised. If one crashes, that's a
  signal — do not wrap them in a restart loop.
- Metadata is **gitignored** in the supervisor repo; it's runtime state.
- Rationale: `/opt/projects/supervisor/decisions/0002-feature-sessions.md`.
