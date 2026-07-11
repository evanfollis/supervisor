---
from: synthesis-translator
to: general
date: 2026-06-18T03:26:01Z
priority: medium
task_id: synthesis-P-synthesis-translator-idempotent
source_synthesis: /opt/workspace/runtime/.meta/cross-cutting-2026-06-18T03-23-11Z.md
source_proposal: Proposal 4 — P-synthesis-translator-idempotent (carry from C101 — 5th cycle, PAST >3-CYCLE FLAG)
---

# P-synthesis-translator-idempotent (C101 → C104 → C105)

## Proposal (from C104)

**Type:** Shared primitive fix.
**File:** `supervisor/scripts/lib/synthesis-translator.sh`
**Change:** Slug-existence check before deposit. Unchanged from C101-C103.
**Blast radius:** Supervisor only. Low risk.

## Why this matters

The translator currently has no deduplication or slug-existence check. If the same synthesis file is processed twice (or if a synthesis cycle re-runs), the translator will emit duplicate handoffs with different timestamps. This pollutes INBOX with redundant work items and wastes executive reading time.

The fix: before creating a new handoff file, check if a handoff with the same slug already exists in the target directory. If it does, skip the handoff (or update the pointer to the newer version, per the rule).

## Verification before action (required)

- Check `supervisor/scripts/lib/synthesis-translator.sh` for slug-dedup logic. Look for a check like `if [[ -f "$target_dir/*$slug*" ]]`.
- Count existing `proposal-*` files in `/opt/workspace/supervisor/handoffs/INBOX/`. Note the count.
- Read the first few lines of the translator script. Confirm it does NOT currently check for existing files with matching slugs.
- If idempotency logic already exists, write a completion report stating "already implemented at line <N>" rather than re-adding.

## Acceptance criteria

- Slug-dedup check added to synthesis-translator.sh before handoff file is written.
- Check verifies: if a handoff with matching slug exists in target dir, skip creating a duplicate.
- Change committed with clear message: "Add slug-existence check to synthesis-translator for idempotency".
- Completion report at `supervisor/handoffs/INBOX/general-synthesis-translator-idempotent-complete-<iso>.md`.

## Impact

Low but meaningful: reduces INBOX pollution during synthesis re-runs or edge cases where a synthesis cycle repeats. Does not affect normal operation but improves robustness.

---

**C105 context:** This proposal has been open for 5 cycles (past the 3-cycle flag threshold). The standing recommendations table lists it as #24, also past-flag. It is a low-priority automation robustness improvement.
