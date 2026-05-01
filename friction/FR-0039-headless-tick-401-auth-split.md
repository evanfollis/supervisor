# FR-0039: Headless project tick 401 auth — interactive sessions unaffected

Captured: 2026-05-01T08:49Z
Source: supervisor-tick, runtime handoff general-context-repo-tick-auth-failure
Status: open

## What happened

All headless project tick sessions (context-repo, command, etc.) fail with
`401 Invalid authentication credentials`. Interactive sessions (reflection
jobs, this supervisor tick) succeed. The failure began 2026-04-30T late and
has persisted across 2+ reflection cycles.

A transient recovery occurred at ~05:13Z on 2026-05-01 (command and context-repo
ticks succeeded briefly), suggesting the key is not simply expired — the
execution path difference is the real issue.

## Why it matters

All autonomous project-level execution is blocked when headless ticks fail. The
workspace's autonomous loop depends on headless ticks for: atlas runner, context-
repo validation cycles, command deploys, synaplex intake. Without headless tick
access, the workspace requires constant attended sessions.

## Root cause / failure class (undiagnosed)

The failing path reads API credentials from a different source than the
reflection path. Candidate sources: env var set only in certain systemd
unit environments, config file not visible to non-interactive shells,
keychain entry accessible only in user sessions.

## Fix needed (operator action required)

1. Compare environment for failing tick unit vs reflection job:
   `systemctl show workspace-reflect.timer | grep Environment`
2. Trace how project tick scripts acquire ANTHROPIC_API_KEY
3. Identify which path has the stale/missing credential and rotate/update it
4. Confirm by running one project tick manually

## Remaining work

Operator access required to inspect systemd unit environments. Cannot diagnose
or fix from an attached Claude session without host-control capability.
