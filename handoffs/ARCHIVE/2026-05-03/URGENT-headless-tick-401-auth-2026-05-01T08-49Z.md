---
type: URGENT
created: 2026-05-01T08:49Z
source: supervisor-tick-2026-05-01T08-49-09Z
priority: critical
fr_ref: friction/FR-0039-headless-tick-401-auth-split.md
consumes:
  - runtime/.handoff/general-context-repo-tick-auth-failure-2026-05-01.md
  - runtime/.handoff/general-server-maintenance-2026-05-01T01-26-04Z.md
---

# URGENT: All headless project ticks failing with 401 auth — operator action required

## Status

Both context-repo tick (2026-05-01T00:38Z) and command tick (2026-05-01T00:51Z)
failed immediately with `401 Invalid authentication credentials`. All subsequent
project tick attempts are blocked. Reflection jobs and atlas runner unaffected.

This is now persistent across 2+ reflection cycles (first seen 2026-04-30T late).

## Why reflection works but ticks don't

The two execution paths acquire credentials differently:
- **Reflection**: runs via `workspace-reflect.timer` → `reflect.sh` → claude session
- **Tick**: runs via project tick scripts → `claude` with different env/config

The failing path likely reads an API key from a different source (env var,
config file, or keychain entry) than the reflection path.

## Operator action required

1. Compare the environment/credential source for the failing tick unit vs. the
   reflection job:
   ```
   systemctl show workspace-reflect.timer | grep Environment
   # vs
   # check how project tick scripts invoke claude
   cat /opt/workspace/supervisor/scripts/lib/tick-*.sh | grep ANTHROPIC
   ```

2. Identify which API key the tick path reads and verify it is valid
3. Rotate or update the stale key in the tick harness config
4. Confirm by running one project tick manually and checking for success

## Server maintenance note

`general-server-maintenance-2026-05-01T01-26-04Z.md` also flagged this as p2
along with LATEST_SYNTHESIS symlink repair. Both are operator-path work.

## Files

- Failed transcript (context-repo): `/root/.claude/projects/-opt-workspace-projects-context-repository/951c44e2-ea19-4551-886a-82cb9b500574.jsonl`
- FR record: `friction/FR-0039-headless-tick-401-auth-split.md`
