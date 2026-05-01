---
id: FR-0039
title: 401 auth credential split — project tick launch path broken, reflection path works
status: Open
created: 2026-05-01
detected-by: cross-cutting-synthesis-2026-05-01T03-27-05Z / server-maintenance-2026-05-01T01-26-04Z
---

# FR-0039: 401 auth credential split blocks all headless project ticks

## What happened

All scheduled project tick sessions (context-repo, command, and implicitly
others) fail immediately with:

> Failed to authenticate. API Error: 401 {"type":"error","error":
> {"type":"authentication_error","message":"Invalid authentication credentials"}}

Reflection jobs running on the same hosts via a different systemd path
(workspace-reflect.timer) succeed within hours of the tick failures. The
atlas runner (separate process, own credential path) also succeeds.

The credential acquisition path for project ticks differs from the
reflection path. The tick path is broken. Reflection path is not.

## Scope

Infrastructure-level. Every project with a scheduled tick session is
affected. This disables the workspace's entire autonomous execution
surface — no unattended code changes, no PM sessions, no project handoff
automation. Only reflection jobs and atlas runner survive.

## Root cause hypothesis

The Claude CLI invocation in the project tick launch script uses a
different API key or auth environment variable than the reflection script.
Likely: key was rotated; reflection script uses a credential source that
was updated (env, file); tick script uses a hardcoded or separately-stored
credential that was not updated.

## Fix direction

1. Compare credential sources: tick script `claude` invocation vs
   `reflect.sh` `claude` invocation — which env var or file does each use?
2. Identify which credential is stale and rotate/refresh it.
3. Add a credential-health preflight to tick launch (attempt a cheap API
   call before processing the handoff; emit URGENT on 401).

This requires operator access to the host credential store.
Server maintenance report filed it as p2: `general-server-maintenance-2026-05-01T01-26-04Z.md`.

## Why no failure event was emitted

The auth failure fires before any tool call, so the session-end summarizer
sees an exit without completing work. The event emitted was
`session_summary_written` (not `failure`). The failing-tick wrapper does
write an URGENT but appears to route it to `runtime/.handoff/` rather than
`INBOX/URGENT-*` (see FR-0038). No monitoring gate fires on this failure class.

## Evidence

- Synthesis: `cross-cutting-2026-05-01T03-27-05Z.md` Pattern 2
- Events: `supervisor-events.jsonl` lines for `project_tick_auth_failed`
- Handoff: `runtime/.handoff/general-context-repo-tick-auth-failure-2026-05-01.md`
- Server maintenance: `runtime/.meta/server-maintenance-2026-05-01T01-26-04Z.md`
