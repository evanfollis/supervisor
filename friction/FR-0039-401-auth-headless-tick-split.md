# FR-0039: Headless project tick 401 auth split

Captured: 2026-05-03T06:50Z
Source: attended-tick-2026-05-03T06-50-00Z
Status: resolved

## What happened

All headless project tick sessions were returning 401 Invalid authentication credentials
starting 2026-04-30. Reflection jobs worked; project ticks (workspace-session@*.service)
did not. Root cause: different credential paths between session types.

## Resolution

Resolved per URGENT-headless-tick-401-auth-2026-05-01T08-49Z.md (archived 2026-05-03T02:47Z).
Ticks confirmed running since 2026-05-03T00:47Z with no further 401 failures in events log.

## Pattern

Reflected a credential-path split between the reflection/synthesis systemd units and the
project session units. When the API key was rotated, only one set of units was updated.
