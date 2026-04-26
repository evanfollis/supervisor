---
id: FR-0039
title: Consecutive tick invocation failures with no escalation path
status: Open
created: 2026-04-26
severity: high
source: supervisor-reflection-2026-04-26T14-27-18Z.md (FR-candidate-J)
---

# FR-0039 — Consecutive tick invocation failures with no escalation path

## Observation

Two Claude invocation failures in 24h: 00:49Z and 12:49Z (Apr 26). Both produced
identical behavior: a 2-line stub tick report, an event note saying "tick claude
invocation failed," and no INBOX diagnostic item. No watchdog monitors failure
cadence as its own escalation class.

## Failure class

One invocation failure can be transient (API rate limit, transient auth). Two in
24h suggests structural fragility: rate limit exhaustion, auth token rotation,
capacity issue, or harness-level regression. The current handling writes a stub
commit and emits a single event — no escalation, no INBOX item, no mechanism to
distinguish "transient" from "structural." The second failure is the trigger that
should fire an URGENT, but no such gate exists.

The tick-invocation-failure-diagnostic proposal in INBOX covers the per-failure
path (write INBOX URGENT on any failure). This FR names the cadence threshold:
2 failures in 24h should escalate with higher priority than a single failure.

## Evidence

- `supervisor-events.jsonl` 00:49Z: `"note":"tick claude invocation failed"`
- `supervisor-events.jsonl` 12:49Z: `"note":"tick claude invocation failed"`
- `supervisor-tick-2026-04-26T00-49-45Z.md`: 2-line stub
- `supervisor-tick-2026-04-26T12-49-43Z.md`: 2-line stub
- No INBOX items from either failure
- No `URGENT-tick-invocation-failed-*` files in INBOX

## Required fix

1. `supervisor-tick.sh`: on invocation failure, write `INBOX/URGENT-tick-invocation-failed-<iso>.md`
   (per proposal-tick-invocation-failure-diagnostic-2026-04-26T03-37-07Z.md).
2. Add cadence gate: if the last 2 tick reports in 24h are stubs, emit a higher-severity
   escalation distinguishing the structural failure class from a transient blip.
3. Do not commit stub output — skip the commit-and-push on invocation failure.
