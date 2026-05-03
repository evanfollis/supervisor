---
name: FR-0039 headless tick 401 auth split
description: Headless project ticks used a different credential path than reflection jobs, causing 401 auth failures from 2026-04-30 through 2026-05-03T00:47Z.
status: resolved
created: 2026-05-01
resolved: 2026-05-03
related:
  - INBOX: URGENT-headless-tick-401-auth-2026-05-01T08-49Z.md (archived)
---

# FR-0039 — Headless project tick 401 auth split

## What happened

From 2026-04-30 through 2026-05-03T00:47Z, all headless project ticks failed with
`401 Invalid authentication credentials`. Reflection jobs continued to work.
Root cause: ticks and reflections used different credential paths; the tick credential
went stale while the reflection credential did not.

## Resolution

Recovered per events at 2026-05-03T00:47Z. URGENT handoff archived. Ticks running clean.

## Status

Resolved. No structural fix documented — the credential rotation process should be
standardized so both paths are refreshed together. See FR-0040/FR-0041 for related
systemic issues.
