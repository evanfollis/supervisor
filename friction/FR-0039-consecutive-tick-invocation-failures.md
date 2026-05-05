---
name: FR-0039 Consecutive tick invocation failures — no diagnostic
description: Two consecutive Claude invocation failures with no wrapper diagnostic, pushing S3-P2 streak to 2/3
type: friction
status: Open
created: 2026-05-05
source: supervisor-tick-2026-05-05T02-47-04Z
priority: medium
---

# FR-0039: Consecutive tick invocation failures — no diagnostic

## What happened

Two consecutive tick sessions failed Claude invocation:
- `2026-05-04T18-50-09Z` — "tick claude invocation failed"
- `2026-05-04T20-49-07Z` — "tick claude invocation failed"

Both emitted `session_reflected` events but no friction records, no diagnostic about *why* invocation failed, and no escalation. The S3-P2 consecutive-failure counter reached 2/3 before the 22:47Z tick succeeded and reset it.

## Evidence

- Events JSONL: `type: session_reflected`, `note: "tick claude invocation failed"` at both timestamps
- No companion `friction_captured` or `escalated` event
- Doctor report at 22:47Z noted the streak

## Root cause

The tick wrapper script (`scripts/lib/supervisor-tick.sh`) detects invocation failure but does not:
1. Log the failure reason (exit code, stderr)
2. Write a friction record automatically
3. Escalate when the streak crosses 2/3

The only visibility is the `session_reflected` event note, which requires reading the full event log to notice.

## Fix direction

The wrapper should capture and log stderr on invocation failure, write a Tier-A friction stub automatically (skipping the claude session), and emit an `escalated` event when the consecutive-failure count reaches 2 (threshold - 1).

## Status

Open. Fix requires change to `scripts/lib/supervisor-tick.sh` (Tier C — attended session). Streak currently at 0 (2026-05-05T00-49-35Z succeeded).
