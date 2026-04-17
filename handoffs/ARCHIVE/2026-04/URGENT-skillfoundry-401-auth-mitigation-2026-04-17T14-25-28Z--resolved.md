# URGENT — skillfoundry tick runner: 401 auth failure escalation absent

**From**: skillfoundry-harness reflection (2026-04-17T14-25-28Z)
**Carry-forward cycles**: 3 (02:22Z Apr 17, 14:23Z Apr 16, prior cycle)
**Threshold**: 3 consecutive cycles without fix commit or decision verdict — escalating per workspace policy

## Problem

When a scheduled PM tick session fails with `Invalid authentication credentials` (401), the session exits silently. No artifact is written. The general session has no way to know the tick failed. Prior incident: c5309767 at 2026-04-16T17:42Z — session exited at line 5 with 401, no escalation handoff written.

## Required fix

In the tick runner script (location: `/opt/workspace/supervisor/scripts/lib/` — confirm exact path), add a post-exit check or `trap ERR` that:
1. Detects 401 output in the session exit
2. Writes `/opt/workspace/runtime/.handoff/URGENT-skillfoundry-auth-failure-<ts>.md` naming the session, timestamp, and exit condition

## Why unblocked

This is a runner script change, not a project code change. It does not affect any harness logic and can be implemented without touching the harness repo.

## Decision needed

Either: (a) implement the escalation hook, or (b) decide explicitly that silent tick failure is acceptable and close this observation with a verdict in `dispositions.jsonl`.
