---
from: synthesis-translator
to: general
date: 2026-05-14T03:31:27Z
priority: medium
task_id: synthesis-inbox-dedup
source_synthesis: /opt/workspace/runtime/.meta/cross-cutting-2026-05-14T03-26-45Z.md
source_proposal: Proposal 3 — Shared primitive — inbox-dedup.sh
---

# Shared primitive: inbox-dedup.sh

INBOX contains two duplicate `proposal-reflect-sh-dirty-tree-*` files (one from cycle 34, one from cycle 35). The dirty-tree detector fires on concurrent autocommit deposits, producing false-positive INBOX items each cycle.

**Purpose:** Deduplicate INBOX by reason-hash before synthesis reads it. Prevents false-positive accumulation.

**Implementation:**

Create `/opt/workspace/supervisor/scripts/lib/inbox-dedup.sh`:

```bash
#!/usr/bin/env bash
# Deduplicate INBOX items sharing the same reason slug (first 40 chars of filename after last timestamp segment)
INBOX="${1:-/opt/workspace/supervisor/handoffs/INBOX}"
cd "$INBOX" || exit 1
ls -1t *.md 2>/dev/null | awk -F'-[0-9]{4}-' '{slug=$1; if(seen[slug]++) print FILENAME}' | while read f; do mv "$f" "${f%.md}.deduped"; done
```

**Behavior:** Scans INBOX for duplicate reason-slugs, renames duplicates (keeping the newest) to `.deduped` suffix. Non-destructive — does not delete, only renames. Can be run manually or wired into synthesis pre-pass.

**Blast radius:** `supervisor/handoffs/INBOX/` only (opt-in). Safe; non-destructive.

## Verification before action (required)

- Check if `inbox-dedup.sh` already exists at the target path
- Verify the awk pattern correctly identifies duplicate reason-slugs from INBOX filenames

## Acceptance criteria

- Script created at `/opt/workspace/supervisor/scripts/lib/inbox-dedup.sh`
- Executable bit set (`chmod +x`)
- Script tested manually on current INBOX (list duplicates without side effects) before commit
- Commit message explains the dedup purpose and false-positive class
- Integration point (synthesis pre-pass or manual invocation) documented in a comment in the script
- Completion report at `runtime/.handoff/general-proposal-inbox-dedup-complete-<iso>.md`

## Escalation

URGENT if:
- The dedup logic produces unexpected collisions (false negatives) when tested on current INBOX. Debug before committing.
