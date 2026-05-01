---
id: FR-0039
title: 401 auth credential split blocks all project ticks
status: Open
created: 2026-05-01
source: supervisor-tick-2026-05-01T06-49-09Z
severity: critical
---

# FR-0039: 401 auth credential split blocks all project ticks

## What happened

Context-repo tick (2026-05-01T00:38Z) and command tick (00:51Z) both failed
immediately with:

> Failed to authenticate. API Error: 401 {"type":"error","error":{"type":"authentication_error","message":"Invalid authentication credentials"}}

Reflection jobs on the same hosts ran successfully within 2 hours. The tick
execution path acquires credentials differently than the reflection path, and the
tick path is broken.

## Impact

All headless project work is blocked: no ticks, no PM sessions, no unattended code
changes for any project. Only reflection jobs and the atlas runner (separate process)
survive. The workspace's entire autonomous execution surface is effectively down.

Context-repo and command ticks subsequently succeeded in the 05:13Z and 05:27Z window
(auth restored by then), but the root cause (why tick vs reflection paths differ) is
unresolved. The gap could recur silently.

## Additional failure

The tick wrapper emitted no `failure` telemetry event on the 401 — it emitted
`session_summary_written`. The monitoring layer received no signal that the credential
path failed. This is invisible-failure compounding: the 401 blocks work AND produces
no distinguishable failure signal.

## Fix class

Operator-level: identify credential acquisition path for tick sessions vs reflection
sessions; pin to the same key or ensure tick harness config reads from the same source.
Add explicit `401` detection in tick wrapper: emit `eventType: "failure"` + create
`INBOX/URGENT-tick-auth-failure-*.md` on 401 exit. See server maintenance handoff
`runtime/.handoff/general-server-maintenance-2026-05-01T01-26-04Z.md`.
