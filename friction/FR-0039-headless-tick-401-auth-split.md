---
id: FR-0039
title: Headless project ticks failing 401 auth — credential path split
status: Open
created: 2026-05-01
severity: critical
projects: all project ticks
---

# FR-0039: Headless project ticks failing 401 auth

## What happened

All headless project ticks (context-repo, command, etc.) have been failing with
`401 Invalid authentication credentials` since ~2026-04-30T late. Reflection jobs
work normally. Atlas tick (which runs differently) unaffected.

First confirmed failure: context-repo tick at 2026-05-01T00:38Z.
Duration: 3+ days as of 2026-05-02.

## Root cause (working hypothesis)

Two code paths acquire API credentials differently:
- Reflection: runs via `workspace-reflect.timer` → `reflect.sh` → `claude -p`
- Project tick: runs via project tick scripts → `claude` with different env/config

One path reads a valid API key; the other reads a stale or missing key. The split
likely appeared when a key was rotated on one path but not the other.

## Fix required (operator action)

1. Compare credential sources:
   ```bash
   cat /opt/workspace/supervisor/scripts/lib/tick-*.sh | grep -E 'ANTHROPIC|API_KEY|claude'
   systemctl show workspace-reflect.timer | grep -i environ
   ```
2. Identify which key the tick path reads; verify it is current
3. Rotate or update the stale key in the tick harness config
4. Confirm by running one project tick manually

## Impact

Zero project ticks have completed since ~2026-04-30. All PM-layer autonomous work
is blocked. Only reflection jobs continue.

## References

- INBOX: URGENT-headless-tick-401-auth-2026-05-01T08-49Z.md
- Failed transcript: `/root/.claude/projects/-opt-workspace-projects-context-repository/951c44e2-ea19-4551-886a-82cb9b500574.jsonl`
