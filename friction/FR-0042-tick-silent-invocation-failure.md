---
name: FR-0042 — Tick silent invocation failure leaves no diagnostic trail
description: The 00:49Z 2026-04-26 tick suffered a Claude invocation failure, committed a 2-line stub, and left no INBOX item, no error capture, and no escalation
status: Open
created: 2026-04-26T02:48Z
discovered-by: supervisor-tick-2026-04-26T02-48-52Z
---

# FR-0042 — Tick silent invocation failure leaves no diagnostic trail

## Status: Open

## Observed behavior

The 2026-04-26T00:49Z supervisor tick produced:
- Tick report: 2 lines only (`_status_: completed (minimal report; model did not write a detailed summary)` / `_doctor_: fail`)
- Event: `"note":"tick claude invocation failed"`
- The tick still committed and pushed (`sha=a50908591fd9`)

No INBOX item. No error capture. No escalation beyond the event string. The substantive tick work — INBOX scan, PM grading, doctor analysis, active-issues sync — did not run.

## Impact

A tick failure is invisible except to someone who reads the tick file or the event note. The next tick has no way to know the previous tick failed, so it treats its own scan as a fresh baseline rather than a catch-up after a missed window.

## Fix required

When the Claude CLI returns a non-zero exit code or produces no output in the tick harness (`supervisor-tick.sh`), the wrapper must:
1. Write a diagnostic INBOX item (not just an event) naming the exit code and any available error output.
2. Emit `tick_failed` event (not `session_reflected` with "completed minimal") — distinguish failure from success.
3. The committed artifact should be tagged as a failure stub, not a normal tick commit.

Tier C work — requires attended session with scripts/lib/ write access.
