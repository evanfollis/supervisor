---
name: FR-0043 consecutive tick invocation failures
description: Two consecutive headless tick sessions (08:47Z and 10:50Z May 3) failed at claude invocation level; pattern broke at 12:48Z but root cause unknown.
status: open
created: 2026-05-03
related:
  - FR-0039-headless-tick-401-auth-split.md
  - FR-0038-ghost-write-event-claims.md
---

# FR-0043 — Consecutive tick claude invocation failures

## What happened

Two consecutive headless tick sessions (2026-05-03T08:47Z and 2026-05-03T10:50Z) failed
at the claude invocation level — not ghost-writes (FR-0038 class) but actual invocation
failures. Both emitted `"tick claude invocation failed"` in events with no substantive
tick output.

The pattern broke at 12:48Z (successful tick) and 14:47Z (this tick). Root cause not
identified.

## Why it matters

Two consecutive invocation failures brought the workspace within one cycle of the S3-P2
`escalated` threshold (N=3). The root cause is unknown — could be rate limiting, API quota,
harness configuration, or network. Without a failure log, future diagnosis is blocked.

## Root cause / failure class

Unknown. The tick event only records `"tick claude invocation failed"` without captured
stderr or exit code. The tick wrapper may not preserve claude's stderr when invocation
fails entirely (vs. ghost-write where the session runs but writes don't persist).

## What's needed

1. Check what the tick wrapper captures when `claude` exits non-zero.
2. Verify API key / rate limit handling in `scripts/lib/supervisor-tick.sh` error path.
3. If pattern recurs (3+ consecutive), surface raw exit code and stderr to tick report.

## Relationship to other FRs

- FR-0038 (ghost-write): sessions invoke successfully but writes don't persist — different.
- FR-0039 (401 auth split): resolved 2026-05-03T00:47Z; may be related if auth degrades again.

## Status

Open — pattern broke but root cause not diagnosed.
