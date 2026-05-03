# FR-0043: Consecutive tick claude invocation failures

Captured: 2026-05-03T12:48Z
Source: supervisor-tick-2026-05-03T12-48-15Z
Status: open

## What happened

Two consecutive headless tick sessions (2026-05-03T08:47Z and 2026-05-03T10:50Z) failed
at the claude invocation level — not ghost-writes (FR-0038 class) but actual invocation
failures. Both emitted `"tick claude invocation failed"` in events with no substantive
output. The 08:47 and 10:50 tick branches were pushed with no Tier-A content changes.

## Why it matters

Two consecutive invocation failures brings the workspace within one cycle of the S3-P2
`escalated` threshold (N=3 consecutive failures). If the 12:48Z tick also fails, S3-P2
fires automatically. The root cause is unknown — could be rate limiting, API quota,
harness configuration, or network — and without a failure log, diagnosis is blocked.

## Root cause / failure class

Unknown. The tick event only records `"tick claude invocation failed"` without a captured
stderr or exit code. The tick wrapper may not be preserving claude's stderr in the tick
report when invocation fails entirely (as opposed to ghost-write, where the session runs
but writes don't persist).

## What's needed

1. Check what the tick wrapper captures when `claude` exits non-zero — compare
   `scripts/lib/supervisor-tick.sh` error path vs. ghost-write path.
2. Verify API key / rate limit status: `claude --version` from the tick user context
   to confirm the harness is reachable.
3. If the pattern continues (3rd consecutive failure), the S3-P2 gate will emit
   `escalated` — at that point the wrapper should surface the raw exit code and stderr
   to the tick report.

## Relationship to other FRs

- FR-0038 (ghost-write): sessions invoke successfully but writes don't persist — different
  failure class than this.
- FR-0039 (401 auth split): resolved 2026-05-03T00:47Z; may be related if auth degraded again.
