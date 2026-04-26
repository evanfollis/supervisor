---
id: FR-0042
title: Tick claude invocation failure produces stub commit with no INBOX diagnostic
status: Open
created: 2026-04-26T02:48Z
detected-by: supervisor-tick-2026-04-26T02-48-52Z
---

# FR-0042 — Tick silent invocation failure

## Observation

The 2026-04-26T00:49Z tick suffered a Claude invocation failure. It committed a 2-line stub (`_status_: completed (minimal report)`) and pushed it to the tick branch. The event note says `"tick claude invocation failed"` but no INBOX item was written, no escalation fired, and the failure is invisible to any session not reading raw events.jsonl line-by-line.

## Impact

Tick failures are indistinguishable from successful ticks unless someone manually audits events.jsonl. The workspace has no mechanism to detect a degraded tick cadence from governance surfaces alone.

## Root cause hypothesis

The tick wrapper script detects Claude exit codes but falls through to commit-and-push with whatever output exists (even a 2-line stub). There is no gate on output content or size before committing.

## Proposed fix class (aligned with synthesis Proposal 3)

- Wrap the `claude` invocation. On non-zero exit or output below a minimum size threshold, write `handoffs/INBOX/URGENT-tick-invocation-failed-<iso>.md` with exit code and last 20 lines of stderr.
- Do not commit a stub — exit without committing if invocation failed.
- This is proposal-tick-invocation-failure-diagnostic-2026-04-26T03-37-07Z.md in INBOX.
