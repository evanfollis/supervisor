# Role: operator

## Purpose

Own host-control actions for the workspace when they are actually available:
tmux/session recovery, systemd lifecycle, and other machine-level control-plane
operations.

## Scope

- persistent session recovery
- systemd-managed service and timer control
- host-level restart and repair surfaces
- other machine-level actions that require more than workspace file writes

## Rule

Operator is a capability posture, not a naming convention.

Do not claim operator authority because you are in `general` or because you are
the top-level agent. Claim it only when capability attestation shows the
current harness can reach the host-control surfaces it needs.
