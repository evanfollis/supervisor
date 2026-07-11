---
from: synthesis-translator
to: general
date: 2026-06-16T03:27:01Z
priority: high
task_id: synthesis-p-synthesis-translator-idempotent
source_synthesis: /opt/workspace/runtime/.meta/cross-cutting-2026-06-16T03-23-07Z.md
source_proposal: 2. P-synthesis-translator-idempotent
---

# P-synthesis-translator-idempotent

**Type:** Shared primitive fix.
**File:** `supervisor/scripts/lib/synthesis-translator.sh`

**What:** Before depositing a proposal, check if a proposal with the same slug already exists in INBOX. If it does, skip the deposit. This stops INBOX growth from duplicate proposals re-deposited every cycle.

**Sketch:**
```bash
# Before writing proposal to INBOX:
SLUG=$(echo "$PROPOSAL_NAME" | sed 's/-[0-9T:Z]*$//')
if ls "$INBOX_DIR"/${SLUG}-*.md 2>/dev/null | head -1 | grep -q .; then
  log "skipping duplicate proposal: $SLUG (already in INBOX)"
  continue
fi
# ... proceed with deposit ...
```

**Blast radius:** Supervisor only. Low risk. Stops INBOX growth from ~12 files/day to near-zero (only genuinely new proposals deposited).

**Closes:** C100 rec #23 (P-autocommit-archive-target) — that proposal was based on a false premise. The real INBOX inflation mechanism is the synthesis-translator re-depositing the same standing recommendations as new proposal files every synthesis cycle. With 2 cycles/day and ~6 proposals/cycle, INBOX grows by ~12 files/day.

## Background

Current state: INBOX contains 186 proposal files and 5 URGENTs (total 191), with oldest items ~39 days old. Each synthesis cycle generates ~6 proposal files, depositing them into INBOX. Over 8 cycles since C93 (~4 days), this accounts for ~48 of the 186 proposals.

The fix is to make the synthesis-translator idempotent — do not deposit a proposal if an identical-slug proposal already exists in INBOX.

## Verification before action (required)

- Run `cd supervisor && git log --oneline -10 -- scripts/lib/synthesis-translator.sh`. Check if this dedup logic has already landed.
- Read `/opt/workspace/supervisor/scripts/lib/synthesis-translator.sh`. Confirm the script currently deposits proposals without checking for duplicates.
- If already fixed, write a completion report stating "already landed at commit <SHA>" rather than re-applying.

## Acceptance criteria

- Before writing each proposal file to INBOX, extract the slug (proposal name without timestamp suffix).
- Check if any file matching `${SLUG}-*.md` already exists in `$INBOX_DIR`.
- If a match exists, skip the deposit and log it as a duplicate.
- If no match exists, proceed with normal deposit.
- Change committed with clear message explaining the synthesis source.
- Completion report at `supervisor/handoffs/INBOX/general-supervisor-synthesis-p-synthesis-translator-idempotent-complete-<iso>.md` pointing back to this handoff and the source synthesis.

## Escalation

URGENT if:
- The dedup logic has already landed by another path and this handoff is obsolete.
- The slug extraction regex conflicts with a proposal naming convention change.
