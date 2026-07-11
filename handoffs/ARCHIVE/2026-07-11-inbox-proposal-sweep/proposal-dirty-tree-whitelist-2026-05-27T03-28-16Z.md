---
from: synthesis-translator
to: general
date: 2026-05-27T03:28:16Z
priority: high
task_id: synthesis-dirty-tree-whitelist
source_synthesis: /opt/workspace/runtime/.meta/cross-cutting-2026-05-27T03-24-35Z.md
source_proposal: Proposal 2 — Dirty-tree check should whitelist known-autocommit targets
---

# Dirty-tree check should whitelist known-autocommit targets

## Summary

Proposal 1 fixes the immediate tick halt by expanding autocommit scope. This proposal eliminates the **failure class**: any future tick-modified file not yet in autocommit's scope will produce the same halt. The fix is to make the dirty-tree check aware of what autocommit is authorized to handle, rather than treating any change as a blocker.

## What to do

Edit `supervisor/scripts/lib/supervisor-tick.sh` to modify the dirty-tree check. Currently it fails if ANY file is modified. Instead, filter out files that `supervisor-autocommit.sh` is authorized to commit, and only fail if OTHER files are dirty.

The whitelist should exclude:
- `events/supervisor-events.jsonl` (written by every tick)
- `handoffs/ARCHIVE/*/session-summary-*.md` (written by autocommit)

Example logic (in the dirty-tree check section, around line 40-60):

```bash
# Get dirty files
DIRTY=$(git -C "$SUP" status --porcelain)

# Filter out files that autocommit will handle
SAFE_DIRTY=$(echo "$DIRTY" | grep -v -E 'events/supervisor-events\.jsonl|handoffs/ARCHIVE/.*/session-summary')

# Only skip if non-safe files are dirty
if [[ -n "$SAFE_DIRTY" ]]; then
  skip_with_reason "working tree contains uncommitted changes outside autocommit scope"
fi
```

## Why this matters

Proposal 1 fixes this specific occurrence. This proposal makes it structurally impossible for any tick-writable file to halt the loop. The whitelist approach clarifies the contract: the tick is allowed to modify certain files, and autocommit is responsible for them. Any other dirty file is a genuine blocker.

This prevents the pattern: "new file is written by tick → autocommit scope hasn't been updated yet → loop halts for N cycles → someone notices → Proposal-1-style fix is written."

## Verification before action (required)

- Confirm the dirty-tree check location: `grep -n "working tree is dirty" /opt/workspace/supervisor/scripts/lib/supervisor-tick.sh`
- Verify the current check is simple and doesn't already have a whitelist
- If whitelist already exists, report "already landed" and stop

## Acceptance criteria

- The dirty-tree check in `supervisor-tick.sh` enumerates the safe files and filters them out
- Change committed with message explaining the structural fix (prevents future similar halts)
- Verify with a test: manually create `events/supervisor-events.jsonl` changes and confirm the tick doesn't skip on that file alone
- Non-safe dirty files should still cause a skip

## Adversarial review recommended

This touches the tick's gating logic. Run `supervisor/scripts/lib/adversarial-review.sh` against the diff before landing.

## Escalation

URGENT if:
- The whitelist filter breaks the dirty-tree gate entirely (e.g. starts ignoring all changes) — revert and investigate
- A tick-writable file is discovered that should be in the whitelist but isn't — add it to the same patch
