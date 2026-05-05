---
id: FR-0039
title: Consecutive tick invocation failures — wrapper emits no diagnostic detail
status: Open
created: 2026-05-05
source: supervisor-tick 2026-05-04T18:49Z and 2026-05-04T20:49Z
---

# FR-0039: Consecutive tick invocation failures

## What happened

Two consecutive tick cycles (2026-05-04T18:49Z and 2026-05-04T20:49Z) failed with `tick claude invocation failed`. The wrapper emitted a `session_reflected` event with that note but no diagnostic detail. The S3-P2 threshold is 3 consecutive failures; at 2/3 the streak reset when the next tick (2026-05-04T22:47Z) succeeded.

## Root cause

Unknown — the wrapper didn't capture or surface the failure reason. Possible causes: API timeout, rate limit, transient auth failure, or OOM. The absence of a diagnostic in the event makes it impossible to distinguish.

## Impact

- Two 2h windows of no supervisor tick work.
- The S3-P2 escalation gate never fired because the streak reset before reaching 3.
- The failure mode is invisible in the event log — downstream sessions can't distinguish "tick skipped" from "tick failed."

## Fix

1. `supervisor-tick.sh` wrapper should capture stderr from `claude -p` and include the first 200 chars in the `session_reflected` event note when invocation fails.
2. Distinguish between different failure types: API error, timeout, rate limit, harness crash.
3. Consider lowering the S3-P2 streak threshold to 2 for rapid-recovery tick failure so it fires before the next success resets the counter.

## Status

Open — fix requires attended session (scripts/lib/ is Tier C).
