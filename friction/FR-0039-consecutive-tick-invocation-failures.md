---
id: FR-0039
title: Consecutive tick invocation failures with no diagnostic output
status: Open
created: 2026-05-04
updated: 2026-05-04
severity: high
---

# FR-0039 — Consecutive tick invocation failures with no diagnostic output

## Problem

Two consecutive supervisor tick sessions (2026-05-04T18:50Z and 2026-05-04T20:49Z)
failed with "claude invocation failed" as the only diagnostic note. No friction
record was written, no URGENT was escalated, and no root cause was identified.
The tick loop continued silently.

## Evidence

From `events/supervisor-events.jsonl`:
```
{"ts":"2026-05-04T18:50:09Z","agent":"tick","type":"session_reflected","note":"tick claude invocation failed"}
{"ts":"2026-05-04T20:49:07Z","agent":"tick","type":"session_reflected","note":"tick claude invocation failed"}
```

No preceding error events, no retry attempts, no URGENT written to INBOX.

## Root cause (hypothesized)

Unknown. Possible causes:
- API rate limiting or quota exceeded
- Network connectivity issue between server and Anthropic API
- Claude Code harness misconfiguration or authentication failure
- Resource exhaustion (memory/CPU) on the host

The tick wrapper (`supervisor-tick.sh`) does not emit a distinct `failure` event
or write an URGENT when claude invocation fails — it falls through to a generic
`session_reflected` note.

## Impact

- Two full tick cycles lost with no governance work
- S3-P2 consecutive-failure threshold (3 same-reason skips → URGENT) not triggered
  because no skip counter is maintained for invocation failures vs. content skips
- Aged INBOX items and tick branches accumulated without notice for 4h

## Fix path

1. Add explicit `failure` eventType emission in tick wrapper when claude exits non-zero
2. Maintain a consecutive-failure counter distinct from consecutive-skip counter
3. Write URGENT to INBOX after 2 consecutive invocation failures (not 3, since these
   are hard failures vs. designed throttling)
4. Add brief diagnostic: capture claude exit code and last N lines of stderr

## Status note

This instance was detected by the 2026-05-04T22:47Z tick session reviewing the
events log. The current run count is 2; one more consecutive failure would cross
the S3-P2 threshold.
