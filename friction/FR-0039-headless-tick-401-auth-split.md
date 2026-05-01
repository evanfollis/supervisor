---
id: FR-0039
title: Headless project ticks failing with 401 auth — reflection path unaffected
status: Open
created: 2026-05-01
source: supervisor-tick-2026-05-01T08-49-09Z (via INBOX)
severity: critical
recurrence: persistent (first seen 2026-04-30 late; transiently resolved at 05:13Z; re-failed at 10:47Z and 12:47Z)
---

# FR-0039: Headless tick 401 auth failure (intermittent root cause undiagnosed)

## What happened

Context-repo and command tick sessions failed with `401 Invalid authentication credentials`
starting 2026-04-30 late. Both resolved transiently at ~05:13Z and 05:27Z on 2026-05-01
(command symphony-lite and context-repo ticks succeeded). Supervisor ticks at 10:47Z
and 12:47Z failed again with 0 tool uses (10 JSONL lines only — likely auth failure
before any tool call).

## Why reflection works but ticks don't

Reflection path (`workspace-reflect.timer → reflect.sh`) acquires credentials differently
from the tick path (project tick scripts → `claude` with different env/config).
Exact credential source for the failing path is unidentified.

## What the transient resolution tells us

The issue is not a permanent key rotation — it resolved and re-failed. Likely cause:
a keyring TTL or environment variable cleared between sessions, or a specific tick
invocation path fails to inherit the credential that the manual/attended path provides.

## Impact

All headless autonomous execution is blocked or intermittent. Only reflection jobs run
reliably unattended. The workspace autonomous execution surface is degraded.

## Required action (operator path)

1. Compare env/credential source: `systemctl show workspace-reflect.timer | grep Environment`
   vs how project tick scripts invoke `claude`.
2. Identify which API key the tick path reads; verify validity.
3. Rotate or update the stale/missing key in the tick harness config.
4. Run one project tick manually and confirm success.

## References

- INBOX: URGENT-headless-tick-401-auth-2026-05-01T08-49Z.md
- Failed transcript: `/root/.claude/projects/-opt-workspace-projects-context-repository/951c44e2-ea19-4551-886a-82cb9b500574.jsonl`
- cross-cutting-2026-05-01T15-28-00Z.md (§Window table, command/context-repo notes)
