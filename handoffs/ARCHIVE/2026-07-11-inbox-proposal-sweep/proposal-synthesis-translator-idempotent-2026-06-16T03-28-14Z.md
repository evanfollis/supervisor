---
from: synthesis-translator
to: general
date: 2026-06-16T03:28:14Z
priority: high
task_id: synthesis-translator-idempotent
source_synthesis: /opt/workspace/runtime/.meta/cross-cutting-2026-06-16T03-23-07Z.md
source_proposal: 2. P-synthesis-translator-idempotent (NEW — replaces C100 rec #23)
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

**Closes:** C100 rec #23 (P-autocommit-archive-target) — that proposal was based on a false premise.

## Background

The synthesis diagnosed that INBOX is inflating because the synthesis-translator re-deposits the same standing recommendations as new proposal files every cycle. With 2 cycles/day and ~6 proposals/cycle, INBOX grows by ~12 files/day. Over 8 cycles (~4 days), this accounts for ~48 of the 186 proposals. This idempotency check stops the growth at the source.

## Verification before action (required)

- Run `git log --oneline -20` on `/opt/workspace/supervisor`. Check if this proposal has already landed via a commit referencing idempotency or translator dedup.
- Read `supervisor/scripts/lib/synthesis-translator.sh`. Check if the idempotency check (SLUG comparison with existing INBOX files) is already implemented.
- If either check shows the fix is already in place, write a completion report stating "already landed at commit <SHA>" rather than re-applying.

## Acceptance criteria

- Idempotency check added to `supervisor/scripts/lib/synthesis-translator.sh` before the deposit step.
- Check uses slug-based matching to prevent duplicate proposals in INBOX.
- Change committed with a message explaining the fix addresses INBOX inflation from re-depositing standing recommendations.
- Completion report at `supervisor/handoffs/ARCHIVE/<iso>/general-synthesis-translator-idempotent-complete.md` pointing back to this handoff and the source synthesis.

## Escalation

URGENT if:
- Verification reveals the fix is already applied. Write a brief completion report and close.
- The translator script has structural changes that make the proposed patch incompatible. Detail the conflict.
