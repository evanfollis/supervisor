---
name: FR-0038-atlas-s3p2-gate-deployed-code-divergence
description: Atlas S3-P2 escalation gate fix committed but not deployed; runner ran 14+ empty cycles with zero alerts
type: friction
status: Resolved
created: 2026-05-02
resolved: 2026-05-02
resolved_by: atlas session restarted service at 14:25:28Z (commit 39b6d2f now live)
---

# FR-0038 — Atlas S3-P2 gate: deployed code diverged from committed code

## What happened

Commit `39b6d2f` replaced the flawed scan-based escalation gate with a persistent counter at `~/.atlas/escalation_state.json`. This fix was merged to main at 2026-05-02T02:11Z. The atlas-runner.service was not restarted. The running service continued on the old scan-based gate for ~12h.

During this window, the atlas runner completed 14+ consecutive empty cycles (`hypotheses_evaluated: 0`) — the exact condition the gate was designed to escalate on. But the gate on the running service used the old scan-based approach, which was blind to midnight-rotation archives. Zero `escalated` events fired.

## Failure class

"Pushed is not deployed" combined with "self-monitoring gate depends on being deployed to work." The workspace already has a rule ("Pushed is not deployed") but the tick sessions that committed the fix lacked `sudo` access to restart the service.

## Status: Resolved

Atlas session restarted `atlas-runner.service` at 14:25:28Z on 2026-05-02. New PID confirmed on `c585891` (which includes `39b6d2f`). Gate re-arms after 3 new empty cycles.

## Systemic fix needed

Tick sessions need a mechanism to trigger service restarts without full sudo. Options: a watched restart-request file that a privileged cron picks up, or sudo rule scoped to `systemctl restart atlas-runner.service`.
