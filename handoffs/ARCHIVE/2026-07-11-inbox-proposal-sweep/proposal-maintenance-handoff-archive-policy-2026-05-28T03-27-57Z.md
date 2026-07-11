---
from: synthesis-translator
to: general
date: 2026-05-28T03:27:57Z
priority: medium
task_id: synthesis-maintenance-handoff-archive-policy
source_synthesis: /opt/workspace/runtime/.meta/cross-cutting-2026-05-28T03-24-25Z.md
source_proposal: C63 Proposal 6 (HYGIENE — dead-letter policy)
---

# Auto-archive aged server-maintenance handoffs

**Type:** Shared primitive addition or CLAUDE.md amendment.

## What

Server-maintenance handoffs older than 7 days in `runtime/.handoff/general-server-maintenance-*.md` should be moved to `runtime/.handoff/.archive/` (or marked `.done`) by the autocommit job or a lightweight cron.

Currently 15 files accumulate (May 15–28) with no consumption path.

Implementation options:
1. **Add logic to supervisor-autocommit.sh** to check age and archive expired maintenance handoffs
2. **Add a policy to CLAUDE.md** designating maintenance handoffs as time-sensitive (auto-expire after 7 days) and have the executive clean them up at reentry
3. **Add a lightweight cron job** to run nightly and archive aged handoffs

Option 1 (integrate into autocommit) is simplest and requires no new cron.

## Why

Nightly maintenance reports are time-sensitive; a 2-week-old maintenance report has no triage value. The accumulation (15 files) inflates the handoff directory and dilutes the signal of genuinely actionable items.

The executive cannot distinguish "needs attention" from "was never read and no longer matters" without reading each file. This is Pattern 1 (diagnostic self-noise) — the monitoring system's output compounds without a consumer.

## Verification before action (required)

- Check if there are already archived maintenance handoffs in `runtime/.handoff/.archive/` (if so, the archive structure exists and can be reused)
- Count current aged files: `ls -1 runtime/.handoff/general-server-maintenance-*.md | xargs -I {} sh -c 'age=$(($(date +%s) - $(date -r {} +%s))); echo "$age {} "' | awk '$1 > 604800 {print $2}'` (7 days = 604800 seconds)
- If cleanup is already happening, write completion report "already actioned" and skip

## Acceptance criteria

- Maintenance handoffs older than 7 days are automatically archived or marked `.done` by autocommit (or cron, per chosen implementation)
- A `.archive/` directory exists in `runtime/.handoff/` with timestamp-organized archives
- The executive can focus on handoffs aged < 7 days without noise from aged items
- Change committed with message explaining the dead-letter hygiene policy
- Completion report includes count of files archived by this change

## Blast radius

`runtime/.handoff/` hygiene only. No project impact. Opt-in: can be a script addition to autocommit or a CLAUDE.md convention with no automation (executive handles it at reentry).

## Escalation

None expected — this is hygiene. If automated, verify it does not delete or archive items that should be retained (check any `.done`-marked files in the archive).
