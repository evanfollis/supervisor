---
name: Headless tick 401 auth — execution path split
description: Headless project ticks fail with 401 auth while reflection jobs succeed — two code paths acquire credentials differently
status: Open
created: 2026-05-01
source: supervisor-tick-2026-05-01T08-49-09Z; INBOX URGENT-headless-tick-401-auth-2026-05-01T08-49Z.md
---

# FR-0039: Headless tick 401 auth — execution path split

## Observation

Headless project ticks (context-repo, command, atlas, supervisor) fail
intermittently with `401 Invalid authentication credentials`. Reflection
jobs running under `workspace-reflect.timer` succeed in the same time window.

Timeline:
- First seen: 2026-04-30T late
- Persistent across 2+ reflection cycles
- Atlas tick failed again at 2026-05-01T21:23:45Z (same 401)
- Supervisor ticks at 10:47Z, 12:47Z, 22:49Z failed silently (0 tool uses)
- Transiently resolved: command and context-repo ticks succeeded 05:13Z–05:27Z

## Why the split matters

The two execution paths likely read credentials from different sources
(env var, config file, or keychain entry). The tick path reads a stale or
missing key. This is not random failure — it is a structural credential
path divergence.

## Operator action required

1. Compare env/credential source: `workspace-reflect.timer` vs project tick scripts
2. Identify which API key the tick path reads and verify validity
3. Rotate/update the stale key in the tick harness config
4. Confirm by running one project tick manually

See INBOX: `URGENT-headless-tick-401-auth-2026-05-01T08-49Z.md`

## Status

Open. Root cause undiagnosed. Requires operator (host-control) access to
inspect systemd unit environments and credential files.
