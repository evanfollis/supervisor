---
from: synthesis-translator
to: general
date: 2026-04-30T15:31:56Z
priority: high
task_id: synthesis-translator-dedup-gate
source_synthesis: /opt/workspace/runtime/.meta/cross-cutting-2026-04-30T15-26-46Z.md
source_proposal: Proposal 2 — Shared primitive — synthesis-translator dedup gate
---

# Synthesis-translator dedup gate

## Summary

Add a deduplication check to `/opt/workspace/supervisor/scripts/lib/synthesis-translator.sh` before writing each proposal to INBOX. This prevents the same proposal from being re-created as duplicate files in consecutive synthesis cycles.

## The problem

Current: synthesis-translator.sh emits one handoff file per proposal in the synthesis, with no check for existing copies. Result:

- `iterate-patch-freeze` proposal now has **5 INBOX copies** (Apr 28 ×2, Apr 29 ×2, Apr 30 ×1)
- `post-action state verification` now has **3 copies** (Apr 29 ×2, Apr 30 ×1)
- `synthesis-translator dedup gate` (the proposal that would fix this) was itself re-emitted as a duplicate INBOX file this cycle

At current accumulation rate (~3 duplicates per 12h cycle), INBOX reaches ~50 items by May 2.

## Proposed fix

Before writing a new proposal to INBOX, compute a stable slug from the proposal title. Check if any file matching `proposal-*"$proposal_key"*` already exists. If yes, skip the write. Pseudocode:

```bash
# For each proposal:
proposal_key=$(echo "$proposal_title" | tr '[:upper:]' '[:lower:]' | sed 's/[^a-z0-9]/-/g' | cut -c1-40)
existing=$(ls "$INBOX_DIR"/proposal-*"$proposal_key"* 2>/dev/null | head -1)
if [[ -n "$existing" ]]; then
  echo "synthesis-translator: skipping duplicate (existing: $existing)" >&2
  continue
fi
# ... emit the proposal to INBOX ...
```

The key is extracted from the title (lowercase, non-alphanumeric → `-`, truncate to 40 chars for filesystem safety). A glob search finds any existing file with that key in its name.

## Verification before action (required)

- Confirm the translator runs via Haiku (claude -p) at the end of synthesize.sh.
- `cat /opt/workspace/supervisor/scripts/lib/synthesis-translator-prompt.md` — verify the prompt guides the translator to emit handoffs.
- `ls -lah /opt/workspace/supervisor/handoffs/INBOX/proposal-* | wc -l` — count current proposals to confirm duplicates exist.
- `grep -c "iterate-patch-freeze" /opt/workspace/supervisor/handoffs/INBOX/proposal-* | sort | uniq -c` — confirm multiple copies of the same proposal.

## Acceptance criteria

- The dedup check is added to synthesis-translator.sh before the `Write` tool call that emits the proposal file.
- The check uses the stable slug approach (title → lowercase/alphanumeric).
- When a duplicate is found, the script logs `"synthesis-translator: skipping duplicate (existing: $path)"` to stderr and continues to the next proposal.
- Commit message: "Add dedup check to synthesis-translator — prevent re-creation of proposals already in INBOX".
- Adversarial review via `supervisor/scripts/lib/adversarial-review.sh` — the dedup logic must handle edge cases (empty titles, special chars, long filenames).
- Completion report at `/opt/workspace/supervisor/handoffs/INBOX/general-synthesis-translator-dedup-complete-2026-04-30T15-31-56Z.md`.

## Expected impact

- Reduces new duplicates from ~3 per cycle to ~0.
- INBOX signal-to-noise improves immediately.
- Archives or bulk-closes existing duplicates are a separate task; this gates future duplicates.

## Escalation

None expected — this is a self-contained script fix with automatic verification (fewer files in INBOX after the next synthesis cycle).
