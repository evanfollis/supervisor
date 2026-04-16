# Persistent session fabric recovery

## Context

The supervisor corrected the workspace-root policy, refreshed runtime health,
removed the old tick hold, and then discovered a deeper live issue: after the
reboot there are no active persistent tmux sessions even though the manifests
under `/opt/workspace/supervisor/sessions/` still say `desired_state: running`.

An attached Codex supervisor session attempted direct recovery using
`/opt/workspace/supervisor/scripts/lib/recover-persistent-sessions.sh`, which
wraps the existing `session-supervisor.sh` mechanism. That failed because the
attached sandbox could not reach the host tmux socket at
`/tmp/tmux-0/default` (`Operation not permitted`).

## State at handoff

- Current docs and current-state surfaces now reflect the real issue.
- A fallback recovery script exists:
  `/opt/workspace/supervisor/scripts/lib/recover-persistent-sessions.sh`
- A friction record exists:
  `/opt/workspace/supervisor/friction/FR-0013-persistent-session-recovery-not-reachable-from-attached-supervisor.md`
- Two stronger PM pressure handoffs were dropped into:
  - `/opt/workspace/runtime/.handoff/context-repo-pressure-current-state-operationalization-2026-04-15T13-53Z.md`
  - `/opt/workspace/runtime/.handoff/command-pressure-git-bootstrap-and-review-enforcement-2026-04-15T13-53Z.md`

## Next action

From a host shell or attached supervisor surface that can actually access tmux:

1. Run `bash /opt/workspace/supervisor/scripts/lib/recover-persistent-sessions.sh`
2. Verify `tmux ls` shows the persistent sessions
3. Verify `/opt/workspace/supervisor/sessions/general.json` now points at
   `/opt/workspace`
4. Let the PM sessions consume the queued runtime handoffs

## Artifacts

- `/opt/workspace/supervisor/system/active-issues.md`
- `/opt/workspace/supervisor/pressure-queue.md`
- `/opt/workspace/runtime/.session-supervisors/manual/logs/general.log`
