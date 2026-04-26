---
name: FR-0039 — consecutive tick invocation failures without escalation path
status: Open
severity: High
created: 2026-04-26
source: supervisor-reflection-2026-04-26T14-27-18Z + synthesis-2026-04-26T15-25-01Z
---

# FR-0039: Consecutive tick invocation failures without escalation path

## Observation

Two tick invocation failures occurred within 24h (2026-04-26T10:50Z and 2026-04-26T12:49Z). The 12:49Z failure produced a 2-line stub report with no INBOX item and no escalation. The wrapper committed the stub as if the tick ran successfully. No mechanism catches N consecutive failures and fires an alert.

## Why it matters

A stuck tick (repeated failures) is indistinguishable from a healthy tick from the outside. The meta-loop depends on ticks running reliably. Silent failures compound: the 12:49Z failure meant one full 2h window produced zero governance work, and no one was notified.

## Fix path

The synthesis proposal (`proposal-tick-invocation-failure-diagnostic-2026-04-26T03-37-07Z.md`) specifies: on invocation failure, write an INBOX item naming the failure and the exact claude command that failed. The wrapper (`supervisor-tick.sh`) should detect an empty/stub report and write the diagnostic item before committing.

## This file

Written on main by an interactive tick session (2026-04-26T20:48Z) to ground-truth this FR. Previous instances exist on tick branches only.
