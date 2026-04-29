---
id: FR-0041
title: .reviews/ directory is read-only in all session types — structural gap
status: Open
created: 2026-04-29T00:47Z
source: supervisor-tick-2026-04-29T00-47-25Z
---

# FR-0041 — .reviews/ permanently read-only; review placement has no execution path

## Observed

`/opt/workspace/supervisor/.reviews/` returns "Read-only file system" on any
write attempt, in both worktree sandbox sessions AND direct non-worktree
sessions. Confirmed via `touch /opt/workspace/supervisor/.reviews/test_write`
returning EROFS in a direct session.

The directory has no bind mount entry in the session sandbox config (unlike
`friction/`, `handoffs/`, `system/`, etc., which are explicitly `rw` mounted).
It is covered by the root overlay which is read-only.

The existing files in `.reviews/` (12 files as of 2026-04-29) were created
before the current filesystem sandbox was applied (oldest dates: 2026-04-17).
New review placement has had no execution path since the sandbox was configured.

## Downstream damage

1. ADR review artifacts cannot be placed in `.reviews/`. Tick `adr-review-complete-0031-0032-2026-04-28T02-49Z.md` has been in INBOX for ~22h with no path to completion.
2. The adversarial review contract (`/review` skill, cross-agent review path) is broken for this repo — review content is generated but cannot be stored in the canonical location.
3. Every tick that runs `/review` will produce content it cannot save, creating a recurring INBOX artifact.

## Fix path

Add `.reviews/` to the supervisor session sandbox's explicit bind-mount list
(alongside `friction/`, `handoffs/`, `events/`, `system/`, `ideas/`).
This requires a change to the supervisor session harness configuration —
Tier-C for the tick, attended session with operator posture needed.

## Workaround

For now, store review content in the INBOX handoff itself and archive after
attended session manually copies to `.reviews/`. This is the current practice
but it creates fake INBOX backlog.
