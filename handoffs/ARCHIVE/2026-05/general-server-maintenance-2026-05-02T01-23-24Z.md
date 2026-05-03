Nightly server maintenance run at 2026-05-02T01-23-24Z produced actionable work.

Core host is stable, but operator follow-up is needed this week: fix recurring 401 auth failures in headless project ticks, repair the LATEST_SYNTHESIS symlink corruption path, and apply routine kernel/OpenSSH package updates in a maintenance window.

Report: /opt/workspace/runtime/.meta/server-maintenance-2026-05-02T01-23-24Z.md

Tasks:
- p2: Restore headless project tick authentication and escalation durability (next maintenance window this week, before relying on project ticks for atlas or other pending handoffs)
- p2: Repair and harden LATEST_SYNTHESIS pointer handling (next maintenance window this week, before relying on LATEST_SYNTHESIS for dispatch decisions)
- p3: Apply routine OS and security updates (routine weekly maintenance window)
