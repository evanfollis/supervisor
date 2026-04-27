---
id: FR-0039
title: Consecutive tick invocation failures without escalation path
severity: HIGH
created: 2026-04-27
status: Open
source: supervisor-tick-2026-04-27T06-48-08Z (written on main; prior instance on ticks/2026-04-26-20)
---

# FR-0039 — Consecutive tick invocation failures without escalation

## Observation

Multiple tick invocation failures have occurred without any escalation path.
The 2026-04-27T00:49Z failure produced a 2-line stub report with no INBOX
item and no diagnostic output. The wrapper committed the stub as if the tick
ran successfully.

## Evidence

- events.jsonl: `2026-04-27T00:48:57Z tick session_reflected "tick claude invocation failed"`
- No INBOX item was written naming the failure.
- Prior failures at 10:50Z and 12:49Z on 2026-04-26 followed the same pattern.
- 3+ failures in 4 days, zero escalations.

## Root cause

The wrapper script (`supervisor-tick.sh`) detects invocation failure but does
not write an INBOX diagnostic item. It commits the stub and exits. No
consecutive-failure counter exists; no threshold triggers an alert.

## Impact

A stuck tick is indistinguishable from a healthy tick from the outside. Silent
failures mean governance windows produce zero work with no notification.

## Fix path

In `supervisor-tick.sh`, on invocation failure: write an INBOX file naming
the failure, the exact claude command that failed, and the exit code. The
synthesis proposal `proposal-tick-invocation-failure-diagnostic-2026-04-26T03-37-07Z.md`
has the full spec. Tier-C (requires attended session edit).
