---
id: FR-0039
slug: headless-tick-401-auth-split
status: open
created: 2026-05-01
discovered-by: supervisor-tick-2026-05-01T08-49-09Z
---

# FR-0039: Headless project ticks fail with 401 auth; reflection jobs succeed

## Symptom

All headless project ticks (context-repo, command, etc.) fail immediately
with `401 Invalid authentication credentials` since 2026-04-30 late.
Reflection jobs continue working. The two execution paths acquire
credentials differently.

## Impact

All project tick sessions are blocked. Autonomous per-project governance
(committing CURRENT_STATE.md, filing FRs, routing handoffs) is unavailable.
Has persisted across 3+ days and multiple operator-blocker escalations.

## Root cause (hypothesis)

The tick path reads an API key from a different source (env var, config file,
or keychain entry) than the reflection path. Likely the `ANTHROPIC_API_KEY`
in the systemd unit environment for ticks differs from the key in
`workspace-reflect.timer`'s environment.

## Fix required

Operator action (compare credential paths; update stale key in tick harness).
See `handoffs/INBOX/URGENT-headless-tick-401-auth-2026-05-01T08-49Z.md` for
exact remediation steps.
