---
from: synthesis-translator
to: general
date: 2026-04-25T03:32:44Z
priority: medium
task_id: synthesis-verified-state-freshness
source_synthesis: /opt/workspace/runtime/.meta/cross-cutting-2026-04-25T03-27-27Z.md
source_proposal: Proposal 4 — Fix verified-state.md freshness gate
---

# Fix verified-state.md freshness gate

## Context

The supervisor charter `/opt/workspace/supervisor/CLAUDE.md` states a freshness requirement: "Freshness requirement — verified-state.md must be <15 min old" (line 207). This gate is critical because principal-facing state claims must rest on current snapshots, not stale data.

However, the current freshness check uses file system mtime (`stat -c %Y`), which is defeated by `supervisor-autocommit.sh`. When autocommit runs `git reset --hard`, mtime updates to current time, making a 29.5-hour-old file appear 12 minutes old. Any principal-facing assertion that triggers a freshness check passes while working from a >24h stale snapshot.

## Proposed Change

**In `supervisor/scripts/lib/verify-state.sh`** — replace the mtime-based freshness check with a content-timestamp parse. The `generated:` field in the file's YAML frontmatter (line 82, currently `generated: $TS`) is authoritative for file age.

Proposed implementation (location: after the section that generates the file, before any principal-facing output that claims state):

```bash
# Current (broken): uses file system mtime, defeated by git reset --hard
# Proposed: parse the generated: frontmatter timestamp for authoritative age

GENERATED_TS=$(grep '^generated:' "$OUT" 2>/dev/null | head -1 | awk '{print $2}')
GENERATED_EPOCH=$(date -d "$GENERATED_TS" +%s 2>/dev/null || echo 0)
NOW_EPOCH=$(date +%s)
STALE_THRESHOLD=900  # 15 minutes, per charter requirement
if (( NOW_EPOCH - GENERATED_EPOCH > STALE_THRESHOLD )); then
  STALE_HOURS=$(( (NOW_EPOCH - GENERATED_EPOCH) / 3600 ))
  echo "WARN: verified-state.md content is ${STALE_HOURS}h stale (generated: $GENERATED_TS)" >&2
fi
```

## Why

The charter rule states <15 min freshness but the check is vulnerable to defeat by git operations that update mtime. A 29.5h stale file passing the gate creates false confidence in state claims. The `generated:` frontmatter is immutable and under content control; mtime is not.

## Acceptance criteria

- Freshness check implementation added to `supervisor/scripts/lib/verify-state.sh`
- Uses the `generated:` YAML frontmatter field, not file system mtime
- Emits a WARN to stderr if content is >15 min old
- Change committed with message explaining the synthesis source
- Completion report at `runtime/.handoff/general-supervisor-synthesis-verified-state-freshness-complete-<iso>.md` pointing back to this handoff and the source synthesis

## Blast radius

**Low.** Only affects the supervisor's own freshness check. No project-level impact. Improves a diagnostic gate; does not change deployed behavior.

## Notes

The threshold (900 seconds = 15 minutes) comes from the charter requirement at `/opt/workspace/supervisor/CLAUDE.md` line 207. If this has been changed, adjust the constant accordingly.
