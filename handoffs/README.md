# Handoffs

Inter-instance handoff channel for the supervisor agent.

This is **not** the `/opt/projects/.handoff/` directory — that one is for
project sessions to hand off to each other and to `general`. This directory
is specifically for the supervisor passing state to its own future self
(possibly running under a different agent harness).

## Flow

1. **Write**: at the end of a session with non-trivial in-flight state, the
   supervisor writes `INBOX/<iso>-<slug>.md` following the handoff template
   (see `AGENT.md` § Handoff contract).
2. **Read**: at the start of every session, the supervisor reads everything
   in `INBOX/`.
3. **Archive**: once acted on, the supervisor moves the handoff to
   `ARCHIVE/YYYY-MM/<filename>`.

## Format

```
# <title>

**From**: <agent> (claude|codex) on <date>
**For**: next supervisor instance
**Context**: <one paragraph — what was being worked on>
**Intent**: <the live mental model or why this mattered, if not obvious from context>

## State at handoff
- Done: ...
- Pending: ...
- Blocked: ...

## Next action
<the single most important thing the next instance should do>

## Artifacts
- /path/to/relevant/file.md
- ...
```

## Retention

`ARCHIVE/` is kept indefinitely — it's the history of how the supervisor has
operated. Storage cost is negligible (markdown text). If the archive gets
unwieldy, collapse a month into a single digest file; don't delete raw entries.

## Style rule

Write for a capable future instance, not for a brittle parser. Keep handoffs
structured, but do not strip away the underlying idea until only procedural
scaffolding remains.

A good default is: note that in every case, the next receiver is a far more
advanced reasoning agent than yourself, then write the handoff as though it
were for a highly intelligent human operator who was not present for the
original conversation. If the handoff would feel patronizing,
over-compressed, or oddly robotic to that reader, it is probably too flattened
for an agent peer as well.
