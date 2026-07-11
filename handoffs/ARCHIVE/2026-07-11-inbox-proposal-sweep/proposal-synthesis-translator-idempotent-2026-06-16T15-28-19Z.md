---
from: synthesis-translator
to: general
date: 2026-06-16T15:28:19Z
priority: high
task_id: synthesis-translator-idempotent
source_synthesis: /opt/workspace/runtime/.meta/cross-cutting-2026-06-16T15-24-30Z.md
source_proposal: 2. P-synthesis-translator-idempotent (carry from C101 — 2nd cycle)
---

# P-synthesis-translator-idempotent: Stop duplicate INBOX proposal files

## Full proposal from synthesis

**Type:** Shared primitive fix.
**File:** `supervisor/scripts/lib/synthesis-translator.sh`

**What:** Before depositing a proposal, check if a proposal with the
same slug already exists in INBOX. If it does, skip the deposit.

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

**Blast radius:** Supervisor only. Low risk. Stops INBOX growth from
~12 files/day to near-zero (only genuinely new proposals deposited).

## Context

Current state: 198 items in INBOX with ~60-70% duplicates. Top duplicated
proposal slugs appear 2-8 times each. The synthesis-translator deposits the
same standing recommendations every cycle because it doesn't check for
existing proposals with the same slug. This creates noise that obscures
genuinely new findings.

## Verification before action (required)

- Check current INBOX size: `ls /opt/workspace/supervisor/handoffs/INBOX/*.md | wc -l`
- Verify duplication: `ls /opt/workspace/supervisor/handoffs/INBOX/*.md | sed 's/-[0-9T:Z]*\.md$//' | sort | uniq -d | head` should show duplicates.
- Confirm the script exists and is callable: `file /opt/workspace/supervisor/scripts/lib/synthesis-translator.sh`

## Acceptance criteria

1. Open `supervisor/scripts/lib/synthesis-translator.sh` (the file that deposits proposals to INBOX).
2. Locate the section where proposals are written to INBOX.
3. Add the slug-existence check before each proposal deposit:
   ```bash
   SLUG=$(echo "$PROPOSAL_NAME" | sed 's/-[0-9T:Z]*$//')
   if ls "$INBOX_DIR"/${SLUG}-*.md 2>/dev/null | head -1 | grep -q .; then
     log "skipping duplicate proposal: $SLUG (already in INBOX)"
     continue
   fi
   ```
4. Commit with message: "Add idempotency check to synthesis-translator; skip duplicate proposals"
5. Verify the fix: run the translator on the next synthesis cycle and confirm INBOX growth is near-zero for proposals (new observations OK; duplicate standing recommendations skipped).

## Escalation

URGENT if:
- The proposal-deposit location is unclear or the script structure has changed. Read the full script first and report the actual deposit pattern.
- After landing this fix, INBOX still grows at >5 files per cycle. This indicates a duplicate source elsewhere (possibly the reflection job itself depositing proposals).

