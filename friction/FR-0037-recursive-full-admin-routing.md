# FR-0037: Recursive "full admin" routing loop

Captured: 2026-04-25T13:20Z
Source: principal
Status: open

## What happened

The principal launched a local Codex session that claimed it lacked authority
and instructed the principal to tmux into the "actual full admin" assistant.
The principal followed that path and reached this workspace-root executive
session, which still attested `operator available: no` because host tmux and
systemd control are blocked by the current harness sandbox.

This produced a circular failure: each agent could plausibly say "not me; use
the full admin session," but no agent actually acquired the missing capability.

## Why it matters

The workspace already separates executive, supervisor, and operator roles, but
the operational behavior still implied that a named session or tmux attachment
could grant host-control authority. That is false. Authority without capability
creates bad routing, stale escalations, and principal busywork.

## Root cause / failure class

ADR-0015 made capability attestation explicit but did not forbid recursive
authority handoff. The system had no crisp rule saying:

- session name is not capability;
- tmux attachment is not capability;
- "open another agent" is not a host-control bridge;
- a blocked agent still owns every reversible action it can perform.

## Fix landed

- `AGENT.md` now includes a "No Recursive Authority Handoff" rule.
- ADR-0015 now has a 2026-04-25 amendment forbidding "full admin" routing as a
  remedy for blocked host control.
- `capability-attestation.sh` now emits `operator handoff: no-agent-route`
  when operator posture is unavailable.
- `active-issues.md` now tracks the remaining structural operator-bridge gap.

## Remaining work

Design and ship a sanctioned operator bridge for host-only actions, or decide
that exact host commands handed to the principal are the explicit bridge for now.
Until then, attached sessions must not pretend another agent session will
magically have more authority.
