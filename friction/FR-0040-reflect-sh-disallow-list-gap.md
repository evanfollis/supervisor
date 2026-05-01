---
name: FR-0040 reflect.sh disallow-list gap
description: reflect.sh's --disallowedTools list does not block Write tool or Bash(python3:*) — reflection sessions can and did mutate project repos, and an unidentified host process ran a git commit command embedded in CURRENT_STATE.md.
status: open
created: 2026-05-01
sources:
  - skillfoundry-harness reflection 2026-05-01T14:26Z
  - general-skillfoundry-harness-reflection-mutated-head-investigation-2026-05-01T14-35Z.md
related:
  - handoffs/INBOX/reflect-sh-disallow-list-gap-2026-05-01T16-48Z.md
---

# FR-0040 — reflect.sh disallow-list gap

## What happened

The skillfoundry-harness reflection session at 2026-05-01T14:26Z mutated
`CURRENT_STATE.md` via the Write tool. Additionally, a commit (`fdbc781`) was triggered
by an unidentified host process that scraped a `git commit -m` command from the
"suggested next action" text in `CURRENT_STATE.md`.

## Two independent failures

**Failure 1 — Write tool not blocked**: reflect.sh's `--disallowedTools` does not include
`Write`, so reflection sessions can write files to the repo they are supposed to only read.

**Failure 2 — Auto-commit of shell commands in CURRENT_STATE.md**: Some host process
(likely a cron or timer) detects `git commit -m "..."` in CURRENT_STATE.md and executes
it. Mechanism unidentified as of this write. This means prose in CURRENT_STATE.md can
become inadvertent shell execution.

## Resolution needed (Tier-C write — operator/attended session)

1. Add to `--disallowedTools` in `scripts/lib/reflect.sh` ~line 108:
   `Write`, `Bash(python3:*)`, `Bash(node:*)`, `Bash(perl -i:*)`, `Bash(sed -i:*)`, `Bash(tee:*)`
2. Adjust reflection report writing: capture to stdout, script persists via `tee`
3. Stop embedding `git commit -m "..."` in CURRENT_STATE.md — replace with prose
4. Identify auto-commit mechanism: `systemctl list-timers --all`, `crontab -l`,
   `find /opt/workspace -name "*.sh" | xargs grep -l CURRENT_STATE`

Ref: `handoffs/INBOX/reflect-sh-disallow-list-gap-2026-05-01T16-48Z.md`

## Status

Open — requires operator edit of scripts/lib/reflect.sh (Tier-C). Routed to attended session.
