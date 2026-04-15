# URGENT: Server Patch + Reboot Overdue

**Created by**: supervisor tick 2026-04-15T10:48:22Z  
**Priority**: HIGH — maintenance window passed, server still degraded

## Situation

The planned 2026-04-15 08:00-09:00 UTC patch-and-reboot window passed without execution. As of 10:48 UTC:

- Server: **REBOOT REQUIRED**, 45 upgradable packages pending
- Kernel: 6.8.0-90-generic running; linux-image-6.8.0-107-generic installed but not yet booted
- Last health snapshot: 2026-04-15T01:25 — no snapshot exists post-08:00 to confirm state changed

## Required actions

1. SSH to the server and execute:
   ```bash
   sudo apt update && sudo apt upgrade -y
   sudo reboot
   ```
2. After reboot, verify: all 4/4 containers healthy, cloudflared active, no failed systemd units.
3. Capture a new health snapshot once the server is back (the nightly job will do this automatically, but a manual check is warranted given the missed window).

## Context

- Scheduled by: `general-server-maintenance-schedule-2026-04-14T14-57-37Z.md` and 5 subsequent handoffs
- Friction record: FR-0009
- Server: Hetzner CPX31, Hillsboro OR (5.78.185.6)

## After completing

Delete all 7 `general-server-maintenance-*` and `general-server-maintenance-schedule-*` and `general-synthesis-*` handoff files from `/opt/workspace/runtime/.handoff/`.
