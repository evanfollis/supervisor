---
name: FR-0039-headless-tick-401-auth-split
description: All headless project ticks fail with 401 auth since 2026-04-30; reflection jobs unaffected — different credential paths
type: friction
status: Open
created: 2026-05-01
---

# FR-0039 — Headless project tick 401 auth split

## What happened

Since approximately 2026-04-30, all headless project tick sessions fail immediately with `401 Invalid authentication credentials`. The reflection job (workspace-reflect.timer) continues to work. The two execution paths acquire credentials differently, and the tick path's credential has gone stale or was invalidated.

## Evidence

- URGENT: `supervisor/handoffs/INBOX/URGENT-headless-tick-401-auth-2026-05-01T08-49Z.md`
- Failed transcript: `/root/.claude/projects/-opt-workspace-projects-context-repository/951c44e2-*.jsonl`
- Reflection jobs continue firing successfully on the same host
- First observed: context-repo tick 2026-05-01T00:38Z and command tick 2026-05-01T00:51Z

## Failure class

Two credential paths for the same underlying API on the same host. When one is rotated/invalidated, the other keeps working — creating the illusion that "Claude is working" while all autonomous project tick sessions are silently failing.

## Status: Open — operator action required

Requires comparing env/config between:
- `workspace-reflect.timer` → what ANTHROPIC_API_KEY source it reads
- Project tick scripts (`supervisor/scripts/lib/tick-*.sh`) → what source they read

Then rotating or updating the stale key in the tick path.
