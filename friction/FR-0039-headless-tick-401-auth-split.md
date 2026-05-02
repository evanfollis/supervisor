---
id: FR-0039
title: Headless project ticks failing with 401 auth — credential path split
status: Open
filed: 2026-05-02
source: supervisor-tick-2026-05-01T08-49-09Z (escalated), written 2026-05-02T06-48Z
projects: all-project-ticks
---

# FR-0039 — Headless project ticks failing with 401 auth

## What happened

All headless project tick sessions fail immediately with `401 Invalid
authentication credentials`. Reflection jobs (workspace-reflect.timer)
and supervisor ticks (Claude-based) are unaffected. The divergence has
persisted 3+ days.

First confirmed: 2026-04-30 late (context-repo and command ticks).
Still failing as of 2026-05-02 (atlas tick confirmed 2026-05-01T21:23Z).

## Why reflection works but project ticks don't

The two execution paths likely acquire credentials from different sources:
- Reflection: workspace-reflect.timer → reflect.sh → claude
- Project tick: per-project tick scripts → `claude` with possibly different env

Hypothesis: the project tick path reads an API key from an env var or config
that was rotated or expired, while the reflection path reads from a different
source (keychain, different env var, different config file).

## Required fix (operator action)

1. Compare credential source for failing tick unit vs reflection job
2. Identify which API key the tick path reads; verify it is valid
3. Rotate or update the stale key in the tick harness config
4. Confirm by running one project tick manually

Reference handoff: `supervisor/handoffs/INBOX/URGENT-headless-tick-401-auth-2026-05-01T08-49Z.md`
