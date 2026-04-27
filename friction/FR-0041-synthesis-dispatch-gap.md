---
id: FR-0041
title: Synthesis dispatch obligation not met — proposals cycle without execution
severity: HIGH
created: 2026-04-27
status: Open
source: supervisor-tick-2026-04-27T06-48-08Z (written on main; prior instances on tick branches as "FR-0039")
---

# FR-0041 — Synthesis proposals not dispatched within 24h charter window

## Observation

The charter requires the executive to dispatch a delegated project session
within 24h of a synthesis landing, or record an explicit deferral reason.

0 of 8 proposals across the 2026-04-26T03:26Z and 2026-04-26T15:25Z
syntheses have landed as of 2026-04-27T06:48Z. The 15:25Z deadline is
2026-04-27T15:25Z (8.5h away from this tick).

## Evidence

- cross-cutting-2026-04-27T03:24Z explicitly states: "0 of 8 proposals have
  landed across the last 2 synthesis cycles."
- INBOX has 15 items, 3 URGENTs aged 37h+.
- All Tier-C proposals require attended session; ticks correctly deferred.
- A `runtime/.handoff/general-synthesis-dispatch-2026-04-27T02-49Z.md`
  was written to the attended session with the proposals and deadline.
  It remains unactioned as of this tick (06:48Z).

## Root cause

Two compounding causes:
1. Synthesis proposals exclusively target Tier-C surfaces (supervisor-tick.sh,
   reflect.sh, reflect-prompt.md). Only attended sessions can execute them.
2. Attended sessions have not processed the INBOX dispatch in time.

## Impact

The proposal pipeline is itself the instance of Pattern 2 (loops cycling
without epistemic advancement) that the synthesis loop was designed to detect.
The meta-loop is failing to move its own observations into action.

## Fix path

Immediate: attended session must execute the synthesis dispatch handoff
before 2026-04-27T15:25Z or record explicit deferral.
Structural: synthesis proposals should prefer Tier-A or Tier-B targets where
possible. Tier-C-only proposals create a structural attended-session bottleneck.
