---
from: synthesis-translator
to: general
date: 2026-05-14T03:31:27Z
priority: high
task_id: synthesis-reflect-sh-archive-filter
source_synthesis: /opt/workspace/runtime/.meta/cross-cutting-2026-05-14T03-26-45Z.md
source_proposal: Proposal 4 — Enforcement gate — reflect.sh dirty-tree false-positive filter
---

# Enforcement gate: reflect.sh dirty-tree false-positive filter

The supervisor reflection and sf-harness reflection both flag that `reflect.sh`'s dirty-tree safety net fires on files deposited by concurrent autocommit in `handoffs/ARCHIVE/`. This produces false-positive URGENTs that consume INBOX capacity.

**Purpose:** Filter `handoffs/ARCHIVE/` from the dirty-tree diff check in `reflect.sh`.

**Target file:** `/opt/workspace/supervisor/scripts/lib/reflect.sh` (around line 112)

**Current code (approximately):**
```bash
DIRTY=$(git diff --name-only HEAD)
if [ -n "$DIRTY" ]; then
  # existing safety-net logic: abort + write handoff
fi
```

**Proposed change:**
```bash
# Exclude known autocommit deposit paths from dirty-tree check
DIRTY=$(git diff --name-only HEAD -- ':!handoffs/ARCHIVE' ':!.reviews')
if [ -n "$DIRTY" ]; then
  # existing safety-net logic: abort + write handoff
fi
```

**Rationale:** `handoffs/ARCHIVE/` is an autocommit deposit surface, not a governance surface. Real mutations that should trigger the safety net occur outside this directory. Filtering reduces false-positive INBOX items without losing actual mutation detection. Related: `inbox-dedup.sh` proposal dedupes the duplicates that accumulate from false positives; this proposal prevents them from being generated in the first place.

## Verification before action (required)

- Read `/opt/workspace/supervisor/scripts/lib/reflect.sh` and locate the dirty-tree check (around line 112)
- Verify current code structure matches the pattern above
- Check if the filter is already in place (grep for `:!handoffs/ARCHIVE`)

## Acceptance criteria

- Code modified at the identified location in `reflect.sh`
- Both `handoffs/ARCHIVE` and `.reviews` excluded from the DIRTY diff (per the proposed code)
- Commit message explains the false-positive class and the reason for each exclusion
- Manual test: run a reflection against a project with deposits in `handoffs/ARCHIVE/` and verify the safety net does not fire
- Completion report at `runtime/.handoff/general-proposal-reflect-sh-archive-filter-complete-<iso>.md`

## Escalation

URGENT if:
- The dirty-tree check uses a different mechanism than `git diff --name-only HEAD` (e.g., uses `git status` or a custom diff tool). Adapt the patch but surface the difference.
- A real mutation under `handoffs/ARCHIVE/` should have been caught by the safety net. Reconsider whether `.reviews` should also be excluded, or if the proposal is incomplete.
