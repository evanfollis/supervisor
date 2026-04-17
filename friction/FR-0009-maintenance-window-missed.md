---
type: friction
id: FR-0009
slug: maintenance-window-missed
date: 2026-04-15
severity: high
status: resolved
---

# FR-0009: Scheduled maintenance window passed without execution

## What happened

The 2026-04-15 08:00-09:00 UTC maintenance window (scheduled by multiple handoffs from 2026-04-14) passed without the planned patch-and-reboot being executed. As of the 10:48 UTC supervisor tick:

- Server health snapshot (2026-04-15T01:25): REBOOT REQUIRED, 45 upgradable packages, kernel 6.8.0-90 running vs 6.8.0-107 available
- No server-health-*.md file from after the maintenance window exists (latest is 01:25)
- No evidence that the patch/reboot was done (server uptime in last snapshot was "5 days, 3 hours, 57 minutes" — still running the old kernel)

The maintenance window recommendation appeared in at least 6 handoffs generated between 2026-04-14T14:55 and 2026-04-15T01:25.

## Why it matters

The server is running a kernel 19 versions behind the installed kernel. Kernel drift is a security and stability exposure. The maintenance system correctly identified and scheduled the work; the gap is in execution — no attended session during the 08:00-09:00 window to act.

## Rule signal

The maintenance pipeline produces correct diagnoses but has no execution path for system-level work (apt upgrade, reboot) that is outside the scope of any agent session. This is a legitimate human-only task. The friction is that the system had no way to escalate "the window is now open" to the principal at the right moment.

**How to apply:** The attended supervisor session should execute the patch-and-reboot now (or schedule an immediate off-hours window). The maintenance pipeline may need a "maintenance SLA missed" alert path distinct from the nightly report.
