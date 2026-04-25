# ADR-0015: Executive/supervisor/operator split and capability attestation
Date: 2026-04-15
Status: accepted

## Context

The workspace overloaded the word `supervisor` to mean three different things:

1. the principal-facing top-level agentic partner
2. the governance/control-plane role
3. the host-control executor for tmux/systemd/server recovery

That ambiguity held until it failed. An attached Codex workspace-root session
could edit `/opt/workspace`, update state, and refine policy, but it could not
reach the host tmux socket or systemd bus. The system still let that session
behave semantically as though it owned the full control plane.

This created a mismatch between claimed authority and verified capability.

## Decision

Adopt an explicit role split:

- **executive** — the principal-facing top-level agentic partner and default
  workspace-root posture
- **supervisor** — the governance, reflection, routing, and policy-refinement
  role
- **operator** — the host-control role for tmux/systemd/session-fabric and
  related machine-level actions

The persistent `general` session remains the canonical workspace-root session
name, but its declared role is now `executive`.

Capability, not name, determines what the top-level session may honestly claim.
Every workspace-root session should perform capability attestation and classify
itself as one of:

- `executive+supervisor+operator`
- `executive+supervisor`
- `project`

An attached workspace-root session that cannot reach host-control surfaces must
degrade explicitly to an attached executive/supervisor posture rather than
continuing to imply full server control.

## Consequences

- The top-level interaction surface matches the principal's intended
  "agentic version of me" model more closely than the old overloaded
  `supervisor` label.
- Governance remains a distinct role rather than collapsing into a vague
  all-powerful session identity.
- Host-control capability becomes inspectable and honest.
- Current-state and bootstrap surfaces must be updated to reflect this role
  split.
- Cross-agent adversarial review is still owed once the persistent session
  fabric is back up; this ADR is accepted on principal direction and live
  evidence from the current harness.

## 2026-04-25 Amendment: no recursive "full admin" routing

The original split was necessary but incomplete. It correctly prevented an
attached session from claiming host control, but it still allowed a circular
failure mode: one attached session could tell Evan to open or tmux into another
agent session that would supposedly have "full admin" authority. If the second
session is launched through the same sandboxed harness, it has the same blocked
host-control capability and repeats the instruction.

Decision:

- Operator posture is not inherited from tmux, session name, cwd, or role
  label. It is granted only by live capability attestation.
- A blocked attached session must not route the principal to another agent as
  the remedy for missing host control.
- The blocked session remains responsible for all reversible work its file and
  repo permissions allow.
- For genuine host-only actions, the correct output is an exact host command or
  sanctioned operator bridge request, not an authority escalation.
- Repeated host-only needs are operator-surface design bugs. They should be
  promoted into scripts, command-surface tools, or another explicit bridge with
  auditable execution semantics.

## Alternatives considered

1. **Keep `supervisor` overloaded and document it better.**
   Rejected: the failure mode is semantic, not editorial.
2. **Make every workspace-root session full operator by policy.**
   Rejected: policy cannot grant capabilities the harness does not have.
3. **Rename everything to `executive` and delete `supervisor`.**
   Rejected: governance and host-control are still distinct and worth naming
   separately.
