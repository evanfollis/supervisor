---
from: synthesis-translator
to: general
date: 2026-06-09T15:31:16Z
priority: medium
task_id: synthesis-translator-dedup
source_synthesis: /opt/workspace/runtime/.meta/cross-cutting-2026-06-09T15-27-48Z.md
source_proposal: P7 — Synthesis translator INBOX dedup
---

# P7 — Synthesis translator INBOX dedup

## Problem

The synthesis translator (`supervisor/scripts/lib/synthesis-translator.sh`) deposits proposals to `supervisor/handoffs/INBOX/` without deduplication. The same proposal (identified by a slug derived from its title) can be deposited multiple times across synthesis cycles if the proposal remains open and unresolved.

Current INBOX growth: **~3 duplicate proposals per cycle** (~6/day).

At this rate, INBOX will exceed 175 items by 2026-06-16 (currently 153 items with zero consumption in 22+ days).

Example: `proposal-reflect-triple-fix-*.md` appears multiple times with different date suffixes (C82, C83, C84, ..., C88), all with identical content, creating dedup noise and degrading signal in an already-saturated queue.

## Solution

Add a slug-based dedup check in `supervisor/scripts/lib/synthesis-translator.sh` before depositing each proposal to INBOX.

For each proposal before creating the handoff file, check if a same-slug item already exists:

```bash
SLUG="proposal-${PROPOSAL_KEY}-*.md"
if ls "$INBOX_DIR"/$SLUG 1>/dev/null 2>&1; then
  echo "translator: skipping duplicate $PROPOSAL_KEY (already in INBOX)" >&2
  continue
fi
```

Where `PROPOSAL_KEY` is derived from the proposal title (e.g., `reflect-triple-fix` from "reflect.sh triple-fix").

This is a **slug-based dedup**, not time-based. A proposal with the same slug is considered a duplicate regardless of when it was created. This allows the translator to skip redeposits of the same unresolved proposal while still allowing legitimate new proposals with different slugs.

## Why this matters

- **Prevents INBOX bloat:** Stops ~3 duplicate proposals per cycle from accumulating (saves ~6 handoff files/day, ~$0.10/day in token cost)
- **Improves signal:** Existing INBOX items remain fresh; new proposals are clearly distinguishable as additions, not reruns
- **Separates concerns:** INBOX hygiene is independent of the three reflect.sh/synthesize.sh fixes and can land in parallel
- **Backwards compatible:** Does not affect proposals already in INBOX; only prevents future duplicates

## Verification before action (required)

- Read `supervisor/scripts/lib/synthesis-translator.sh` and locate where handoff files are written to INBOX
- Verify the slug derivation logic (how proposal keys are extracted from proposal titles)
- Check the INBOX directory to understand the current slug patterns and confirm duplicates exist

## Acceptance criteria

- Dedup logic inserted into synthesis-translator.sh before each INBOX file creation (~5 lines)
- Change committed with message explaining duplicate suppression
- Run one full synthesis cycle and verify:
  - No duplicate `proposal-*-*.md` files are deposited to INBOX for proposals that already exist
  - New proposals with new slugs are still deposited normally
- Completion report notes the confirmed dedup behavior

## Blast radius

Synthesis translator only (automatic). Reduces INBOX growth from ~3/cycle to ~0/cycle (for unresolved proposals). Does not affect project sessions or proposal execution.

## Escalation

URGENT if:
- A proposal has already been updated/superseded in the same synthesis run (e.g., P1 exists in INBOX from C70, but C88 proposes P1 with new content). In this case, dedup is too aggressive — escalate as a proposal-versioning gap rather than skipping it.
- The slug derivation is ambiguous (two proposals with the same slug but different content). Clarify the slug space before landing.
