---
name: FR-0038
slug: consecutive-tick-invocation-failures
status: Open
created: 2026-04-30
source: supervisor-tick-2026-04-30T14-49-54Z
---

# FR-0038 — Consecutive tick invocation failures (10:48Z and 12:47Z)

## What happened

Two consecutive automated tick sessions failed to invoke the Claude model:
- `supervisor-tick-2026-04-30T10-48-56Z`: event note "tick claude invocation failed"
- `supervisor-tick-2026-04-30T12-47-54Z`: event note "tick claude invocation failed"

Both produced stub reports (`_status_: completed (minimal report; model did not write a detailed summary)`).
The 14:49Z tick (this session) was a direct interactive invocation that succeeded.

## Why it matters

Two consecutive failures = S3-P2 escalation threshold. The workspace has no signal on what caused the failures (rate limit, timeout, harness crash, API error). The tick wrapper emits only "tick claude invocation failed" with no cause detail. Without root cause, the failure class cannot be eliminated.

## Root cause hypothesis

Unknown. Possibilities: Claude API rate limit hit by concurrent session load, harness crash mid-invocation, network hiccup. No diagnostic data in the tick stubs.

## What would fix it

Tick wrapper should capture and log the Claude invocation exit code and stderr to the tick report, not just emit a one-line failure note. This enables distinguishing: rate-limit (429), auth failure (401), timeout, or harness crash.

## Status

Open — root cause unknown. Proposal `proposal-tick-consecutive-failure-tracking-2026-04-29T15-29-09Z.md` in INBOX already addresses this; needs attended session to implement in scripts/lib/.
