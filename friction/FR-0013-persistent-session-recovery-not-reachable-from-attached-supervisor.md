# FR-0013: Persistent session recovery is not reachable from attached supervisor

Captured: 2026-04-15
Source: session
Status: open

## What happened

After the reboot, the persistent session fabric was down: there were no live
tmux sessions for `general`, `mentor`, `skillfoundry`, `recruiter`,
`context-repo`, `command`, or `atlas`, even though the manifests under
`/opt/workspace/supervisor/sessions/` still claimed `desired_state: running`.

The supervisor corrected the launch-root policy and added a sandbox-safe
recovery wrapper at
`/opt/workspace/supervisor/scripts/lib/recover-persistent-sessions.sh`, then
attempted to repopulate the sessions by invoking the existing
`session-supervisor.sh` mechanism through detached restart loops.

That recovery failed immediately because the attached Codex harness could not
talk to the host tmux socket:

- `tmux ls` -> `error connecting to /tmp/tmux-0/default (Operation not permitted)`
- every recovery log under
  `/opt/workspace/runtime/.session-supervisors/manual/logs/*.log` showed the
  same failure

The retry loops were then stopped to avoid pointless churn.

## Why it matters

The supervisor cannot actually push the PM layer upward if the PM/session layer
is absent and the attached supervisor cannot restore it. That leaves the
principal as the recovery mechanism after reboots or session-fabric collapse,
which is the opposite of the intended stack progression.

## Root cause / failure class

The system assumes that the same surface used for supervisor work can also
recover tmux-backed persistent sessions. In practice, attached sandboxed Codex
can write workspace files but may still be unable to reach host-control
surfaces like systemd or tmux sockets.

This is a mechanism gap, not just a documentation gap:

- policy said the supervisor owns the control plane
- documented recovery relied on systemd/tmux
- the attached harness did not have access to either recovery surface

## Proposed fix

One of these needs to become true:

1. The normal attached supervisor harness gets sanctioned access to the host
   tmux/session recovery surface.
2. A host-side recovery command is exposed as an explicit, durable part of the
   supervisor contract and current-state bundle.
3. The persistent session layer migrates to a recovery surface the attached
   supervisor can actually control.

Until then, session-fabric recovery should remain an explicit active issue and
pressure item, not an implicit assumption.

## References

- `/opt/workspace/supervisor/scripts/lib/recover-persistent-sessions.sh`
- `/opt/workspace/supervisor/scripts/lib/session-supervisor.sh`
- `/opt/workspace/supervisor/system/active-issues.md`
- `/opt/workspace/supervisor/pressure-queue.md`
- `/opt/workspace/runtime/.session-supervisors/manual/logs/general.log`
