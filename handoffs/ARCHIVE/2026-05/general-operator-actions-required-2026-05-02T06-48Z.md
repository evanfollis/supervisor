---
from: supervisor-tick-2026-05-02T06-48-26Z
to: general
date: 2026-05-02T06:48Z
topic: operator actions required — auth fix + atlas restart + server maintenance
priority: high
---

# Operator actions required — 2026-05-02

Three items require operator-level host control. All are blocked from tick sessions.

## 1. Fix headless project tick 401 auth (CRITICAL)

All headless project ticks have been failing with `401 Invalid authentication credentials`
since 2026-04-30. Reflection jobs work; ticks don't. Root cause: different credential paths.

```bash
# Compare credential sources
cat /opt/workspace/supervisor/scripts/lib/tick-*.sh | grep -E 'ANTHROPIC|API_KEY|claude'
systemctl show workspace-reflect.timer | grep -i environ
# Check environment of the failing unit
systemctl show workspace-session@atlas.service | grep -i environ
```

Then rotate/update the stale key and run one project tick manually to confirm.
FR: `supervisor/friction/FR-0039-headless-tick-401-auth-split.md`
INBOX: `supervisor/handoffs/INBOX/URGENT-headless-tick-401-auth-2026-05-01T08-49Z.md`

## 2. Restart atlas runner (HIGH)

Commit `39b6d2f` (S3-P2 frozen-loop gate fix, 156/156 tests pass) is deployed to main
but the service has not been restarted.

```bash
sudo systemctl restart atlas-runner.service
journalctl -u atlas-runner.service -n 10 --no-pager
```

After restart: gate re-arms after ~3 empty cycles (~3h at hourly cadence).
Handoff: `runtime/.handoff/general-atlas-s3p2-restart-needed-2026-05-02T04-47Z.md`

## 3. Server maintenance (p2-p3)

From nightly maintenance report 2026-05-02T01:23Z:
- p2: Repair LATEST_SYNTHESIS symlink corruption path
- p3: Apply routine OS and security updates (kernel/OpenSSH)

Report: `/opt/workspace/runtime/.meta/server-maintenance-2026-05-02T01-23-24Z.md`
