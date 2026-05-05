---
id: FR-0039
title: Consecutive tick claude invocation failures
status: Open
filed: 2026-05-05T10-47-35Z
source: supervisor-tick-2026-05-05T10-47-35Z
severity: high
---

# FR-0039: Consecutive tick claude invocation failures

## Observed failure

Two consecutive tick slots (06:48Z and 08:49Z on 2026-05-05) produced only:

```
_status_: completed (minimal report; model did not write a detailed summary)
_doctor_: fail
```

The claude invocation in the tick wrapper failed for both slots. This is the third
occurrence of this pattern — prior occurrences were noted in tick events but the
FRs capturing the pattern were ghost-written (see FR-0038).

## Evidence

- `/opt/workspace/runtime/.meta/supervisor-tick-2026-05-05T06-48-26Z.md`: minimal stub
- `/opt/workspace/runtime/.meta/supervisor-tick-2026-05-05T08-49-53Z.md`: minimal stub
- `events/supervisor-events.jsonl`: both slots show "tick claude invocation failed" note in wrapper emit

## Impact

Each failed tick means 2h of governance dead time. Consecutive failures mean 4h+.
The S3-P2 rule requires escalation after 3 consecutive same-reason skips; this is
approaching that threshold.

## Required fix

1. The tick wrapper should capture stderr from the `claude` invocation and include it
   in the stub tick report, enabling diagnosis without a separate attended investigation.
2. After 2 consecutive failures, the wrapper should emit an URGENT handoff to
   `supervisor/handoffs/INBOX/` naming the failure mode and the last known error.

## How to apply

When reviewing a tick report showing "minimal report; model did not write a detailed
summary" — treat it as a diagnostic signal, not a low-quality tick. Check the prior
slot's stub for the same pattern; 2 consecutive = escalate to INBOX.
