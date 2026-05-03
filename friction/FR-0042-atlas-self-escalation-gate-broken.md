---
name: FR-0042 — Atlas S3-P2 self-escalation gate suppressed by stale last_emitted_ts
status: Resolved
filed: 2026-05-02 (ghost-claim); written to disk 2026-05-03
source: atlas-reflection-2026-05-02T14-18-55Z.md; cross-cutting-synthesis-2026-05-02T15-27Z
resolved: Counter-based gate (commit 39b6d2f) deployed via systemctl restart at 14:25Z May 2
---

# FR-0042 — Atlas S3-P2 self-escalation gate suppressed by stale last_emitted_ts

## Pattern

The atlas runner was producing `hypotheses_evaluated: 0` on every cycle since A+C+D2 deploy
(~May 1). The existing scan-based S3-P2 gate that should fire `cycle.escalated` after N
consecutive empty cycles was suppressed by a stale `last_emitted_ts: 1777332686393`
(2026-04-27T02:31Z). The gate concluded the current empty run was a continuation of an already-
escalated Apr 27 streak and suppressed new escalation signals.

## Evidence

- Atlas telemetry: 14+ consecutive `cycle.completed` events with `hypotheses_evaluated: 0`,
  no `cycle.escalated` event between Apr 27 and May 2 14:25Z deployment.
- Reflection 2026-05-02T02:18Z: "The gate has not fired since Apr 27 even though the runner
  has been stuck for ~90+h."
- The system was in the worst possible state: zero scientific output AND zero alerts.

## Why it matters

A self-monitoring gate that doesn't fire on frozen state is indistinguishable from no gate
at all. The workspace rule (CLAUDE.md §Self-monitoring) requires self-reporting of stuck
states. The scan-based gate violated this by silently suppressing after the first escalation.

## Fix

Commit 39b6d2f replaced the scan-based gate with a persistent counter that increments on
every empty cycle, regardless of prior escalation history. Deployed via
`sudo systemctl restart atlas-runner.service` at 14:25Z May 2. Verified: `cycle.escalated`
events now appearing in telemetry (consecutive_cycles counting correctly).

## Status

Resolved. Counter-based gate deployed and verified. P1 (TESTING orphan re-evaluation) is
implemented (commit 71224e9) but requires a separate service restart to activate.
