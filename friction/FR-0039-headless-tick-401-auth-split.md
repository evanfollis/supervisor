---
name: FR-0039 headless tick 401 auth split
description: Headless project ticks fail with 401 Invalid authentication credentials while interactive sessions (reflection, attended supervisor) succeed — credential source divergence between execution paths.
status: open
created: 2026-05-01
sources:
  - context-repo tick 2026-05-01T00:38Z (first 401)
  - command tick 2026-05-01T00:51Z (second 401)
  - supervisor ticks 10:47Z and 12:47Z (silent fail, 0 tool uses)
related:
  - URGENT-headless-tick-401-auth-2026-05-01T08-49Z.md
  - friction/FR-0038-ghost-write-event-claims.md
---

# FR-0039 — Headless tick 401 auth split

## What happened

All scheduled project ticks began failing with `401 Invalid authentication credentials`
starting 2026-04-30T late. Interactive sessions (reflection jobs, attended supervisor ticks)
remain functional. The two execution paths acquire credentials differently.

Timeline:
- 2026-04-30T late: first failures observed
- 2026-05-01T00:38Z: context-repo tick fails with 401
- 2026-05-01T00:51Z: command tick fails with 401
- 2026-05-01T05:13Z: context-repo tick succeeds (transient recovery?)
- 2026-05-01T10:47Z, 12:47Z: supervisor ticks fail silently (0 tool uses)
- 2026-05-01T16:48Z: supervisor tick succeeds as interactive session

## Root cause (suspected)

The headless path reads an API key from a different source than the interactive path.
Candidates: env var in the headless unit vs. keychain/config for interactive; stale key
in one source after rotation.

## Operator steps needed

1. Compare credential source: `systemctl show workspace-session@<project>.service | grep Environment`
   vs. how the interactive session's claude invocation sources the key
2. Identify which API key the headless tick path reads
3. Verify the key is valid; rotate/update if not
4. Confirm by running one project tick manually

## Status

Open — 401 root cause undiagnosed as of 2026-05-01T18:47Z. Transient recovery at 05:13Z
complicates diagnosis. Operator action required (principal).
