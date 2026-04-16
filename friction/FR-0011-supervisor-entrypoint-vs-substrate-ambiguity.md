# FR-0011: Supervisor entrypoint and substrate were described as different roots

Captured: 2026-04-15
Source: principal + attended supervisor session
Status: mitigated

## What happened

The workspace policy said a session rooted at `/opt/workspace` defaults to the
supervisor role, but the bootstrap text and parts of the live control-plane
still described the supervisor as something that should "operate from"
`/opt/workspace/supervisor`.

That ambiguity was strong enough that an attended Codex session concluded its
write boundary was self-limited by launch cwd rather than by the actual
workspace topology. The result was wasted diagnosis, a false permissions
theory, and stale control-plane state surviving longer than necessary.

## Why it matters

For the supervisor, path semantics are governance semantics. If launch root,
durable repo, and runtime state are not stated unambiguously, the agent can
misclassify its authority, skip valid actions, or reason from the wrong truth
surface under pressure.

This is not just documentation polish. It directly affects whether the control
plane compounds learning or stalls behind invented boundaries.

## Root cause / failure class

**Entry point and substrate were being treated as synonyms.**

They are not:
- `/opt/workspace` is the supervisor launch root
- `/opt/workspace/supervisor` is the durable governance repo
- `/opt/workspace/runtime` is generated state

When those roles blur, the agent has to infer architecture from fragments of
text and live state instead of reading one coherent contract.

## Proposed fix

1. Make the root workspace policy state the three surfaces explicitly.
2. Make `supervisor/AGENT.md` define entrypoint vs. substrate directly.
3. Keep tick/trace logic compatible with both `/opt/workspace` and legacy
   `/opt/workspace/supervisor` until the persistent `general` session is
   restarted and its manifest updates.
4. Leave this friction record in place even after the restart so the failure
   class stays visible.

## References

- `/opt/workspace/AGENTS.md`
- `/opt/workspace/CLAUDE.md`
- `/opt/workspace/supervisor/AGENT.md`
- `/opt/workspace/supervisor/scripts/lib/sessions.conf`
- `/opt/workspace/supervisor/sessions/general.json`
