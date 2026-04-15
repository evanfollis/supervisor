# Enforcement Model

The goal is not perfect prevention. The goal is to make the intended governance
path the easiest path, keep bypasses visible, and reserve heavier controls for
when the lighter ones stop being sufficient.

## Present controls

Before this change, the workspace already had:

- systemd-supervised persistent sessions
- a dedicated supervisor repo
- append-only supervisor events
- scheduled reflections and synthesis
- runtime handoff channels

These made the control plane durable, but not yet self-identifying or
fully aware of direct lower-layer interaction.

## Controls added by this change

### 1. Workspace-root defaults to supervisor behavior

Any session started at `/opt/workspace` should be treated as supervisory by
default. This makes the easy path line up with the intended architecture.

### 2. Session roles are explicit

Persistent session registry now declares role directly. The system no longer
has to infer "general is probably the supervisor" from naming convention alone.

### 3. Transcript normalization is always on

A systemd timer scans durable Claude and Codex transcripts and writes a
normalized session trace. This gives the supervisor post-hoc awareness even
when the principal speaks directly to a project or feature session.

## What this enforces well

- default identity at the workspace root
- durable visibility into direct human interaction across layers
- a single control-plane record of who talked where and when
- low-friction recovery after session crashes or detached conversations

## What remains soft

- the supervisor can still be instructed to violate its boundary if the human
  insists
- project sessions still rely on prompt and repo-local policy for most conduct
- nothing here prevents a human from opening an arbitrary ad hoc session in an
  arbitrary cwd

That softness is intentional for now. The system responds by making bypasses
legible, not by pretending they cannot happen.

## Future hardening options

If stronger enforcement becomes necessary, add these in order:

### 1. Separate OS identities

Run supervisor and project sessions as different Unix users so the supervisor
cannot casually mutate project repos.

### 2. Brokered delegation

Require workspace-level mutations to enter projects through a handoff broker or
controlled feature-session opener instead of direct repo access.

### 3. Path-based write restrictions

Constrain the supervisor harness so it can write only to `supervisor/` and
`runtime/`, not to `projects/`.

### 4. Escalation-gated boundary expansion

Require explicit principal approval before a lower layer receives expanded
authority in a new class of decisions.

## Design test

If the easier path under stress is still "open the workspace root and talk to
the meta layer," the design is working.

If the easier path becomes "skip the control plane and hope it catches up
later," the design needs harder boundaries.
