---
name: Headless tick 401 auth split
status: Open
created: 2026-05-01
source: context-repository-reflection-2026-05-01T02-38-03Z / command-reflection-2026-05-01T02-35-49Z
severity: critical
---

# FR-0039: Headless project tick sessions fail with 401 while reflection jobs succeed

## What happened

Context-repo tick (2026-05-01T00:38Z) and command tick (2026-05-01T00:51Z) both
failed immediately with:

> Failed to authenticate. API Error: 401 {"type":"error","error":{"type":"authentication_error","message":"Invalid authentication credentials"}}

Reflection jobs on the same host, executed within 2 hours via a different
systemd path, succeeded. The atlas runner (separate process) also continues
running.

## Why it matters

All headless project work is blocked. No project ticks, no PM sessions, no
unattended code changes can succeed through the tick path. Only reflection jobs
and the atlas runner survive. The workspace's entire autonomous execution surface
is degraded.

## Root cause candidates

- Tick sessions use a different credential source (env var, keychain, API key
  file) than reflection jobs
- An API key used by tick sessions was rotated or expired without updating the
  tick harness config
- The tick launch path (systemd unit) does not inherit the credential env that
  reflection jobs receive

## Remediation

Operator action: compare the env/credential source used by the failing tick
systemd unit against the successful reflection job path. Rotate or update
whichever key the tick path reads. This is a host-control action requiring
operator posture.
