---
name: FR-0039 — Headless project ticks failing with 401 auth while reflection jobs succeed
status: Resolved
filed: 2026-05-01 (ghost-claim); written to disk 2026-05-03
source: supervisor-tick-2026-05-01T08-49Z (URGENT-headless-tick-401-auth-2026-05-01T08-49Z.md)
resolved: 2026-05-03 (ticks recovering per events log — atlas tick succeeded at 01:14Z May 3)
---

# FR-0039 — Headless project ticks failing with 401 auth while reflection jobs succeed

## Pattern

Both context-repo tick (2026-05-01T00:38Z) and command tick (2026-05-01T00:51Z) failed with
`401 Invalid authentication credentials`. Reflection jobs (workspace-reflect.timer) were
unaffected in the same window. This split suggested the two execution paths read API keys
from different sources.

## Evidence

- `events/supervisor-events.jsonl` shows `project_tick_auth_failed` for atlas at 21:01:57Z
  May 2 and for context-repo/command at May 1 00:38Z / 00:51Z.
- Reflection jobs ran successfully in the same windows.
- `general-server-maintenance-schedule-2026-05-03T02-06-47Z.md`: "Headless project tick 401
  failures recovered by 2026-05-03, keep on watch rather than scheduling repair work."
- Atlas tick succeeded at 01:14Z May 3 (confirmed in events log).

## Why it matters

401 auth on project ticks blocks all delegated project work from executing autonomously.
The workspace's autonomous capacity collapses to reflection-only.

## Root cause (unresolved at time of filing)

The failing path likely reads an API key from a different source than the reflection path.
The credential source split was not diagnosed before recovery. If auth fails again, compare:
```
cat /opt/workspace/supervisor/scripts/lib/tick-*.sh | grep ANTHROPIC
systemctl show workspace-reflect.timer | grep Environment
```

## Status

Resolved (ticks recovered by 2026-05-03). Root cause not formally diagnosed — if recurrence,
diagnose the credential-source split before rotating keys.
