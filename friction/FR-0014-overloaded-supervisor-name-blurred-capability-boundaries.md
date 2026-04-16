# FR-0014: Overloaded "supervisor" name blurred capability boundaries

Captured: 2026-04-15
Source: principal
Status: open

## What happened

The workspace used `supervisor` to mean both:

- the principal-facing top-level doer
- the governance/control-plane role
- and, implicitly, the host-control executor

That made it too easy for an attached workspace-root session to sound like it
owned the entire server even when it lacked tmux/systemd access.

## Why it matters

When the name of the role implies more authority than the current harness can
actually exercise, the principal gets a misleading interaction surface and the
agent gets pushed into explanation instead of honest, capability-aware action.

## Root cause / failure class

Role identity was being inferred from session naming convention rather than
verified capability and declared posture.

## Proposed fix

Adopt an explicit split:

- `executive` for the principal-facing top layer
- `supervisor` for governance/policy
- `operator` for host-control

Then require capability attestation at session start.

## References

- `/opt/workspace/supervisor/decisions/0015-executive-supervisor-operator-split-and-capability-attestation.md`
- `/opt/workspace/supervisor/friction/FR-0013-persistent-session-recovery-not-reachable-from-attached-supervisor.md`
