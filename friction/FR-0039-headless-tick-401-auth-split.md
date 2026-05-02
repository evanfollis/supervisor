---
id: FR-0039
title: Headless project ticks fail 401 — credential path diverges from reflection jobs
status: Open
created: 2026-04-30
updated: 2026-05-02
source: URGENT-headless-tick-401-auth-2026-05-01T08-49Z
---

# FR-0039: Headless project tick 401 auth split

## What happened

All headless project ticks began failing with `401 Invalid authentication
credentials` starting 2026-04-30 (late). Reflection jobs (workspace-reflect.timer)
continued to work. The two execution paths acquire the Anthropic API key from
different sources — the reflection path reads from one location; the tick path
reads from another, and that second location holds a stale or missing key.

As of 2026-05-02T14:50Z this has been broken for ~3 days.

## Why it matters

Project ticks are the primary execution path for PM-layer work. When they fail
with 401, all project-session code work stops. Reflection continues (giving false
confidence) while actual forward progress halts. The two-path credential model
was not intentional design — it emerged from how the systemd units were wired
and has never been reconciled.

## Fix direction

1. Identify which credential source each path uses (env var vs config file vs
   keychain) by comparing the two unit environments
2. Unify to a single path — preferably the env var that reflection already uses
3. Confirm with one manual project tick run

## Operator actions pending

See `handoffs/INBOX/URGENT-headless-tick-401-auth-2026-05-01T08-49Z.md` and
`runtime/.handoff/general-operator-actions-required-2026-05-02T06-48Z.md`.
