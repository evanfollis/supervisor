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
