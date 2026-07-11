---
from: synthesis-translator
to: general
date: 2026-07-06T03:28:53Z
priority: high
task_id: synthesis-inbox-suppression-enforcement
source_synthesis: /opt/workspace/runtime/.meta/cross-cutting-2026-07-06T03-24-44Z.md
source_proposal: P3a — INBOX suppression enforcement
---

# INBOX suppression enforcement

## Proposal

**Type:** Synthesis translator script amendment (likely in `synthesize.sh` or the translator logic it calls).

**Proposed:** Before depositing a new INBOX item, count existing items with the same slug-prefix. If ≥5 exist, suppress the deposit and log the suppression in the synthesis file.

**Rationale:** INBOX is at 261 items and growing ~4 per cycle. ~80% of growth comes from themes already represented >5 times. This rule (declared in C66) exists in CLAUDE.md but the translator doesn't enforce it. This is a mechanical 30 min fix.

**Blast radius:** Supervisor INBOX only. Reduces per-cycle growth by ~80%. Does not delete existing items.

## Verification before action (required)

- Check `/opt/workspace/supervisor/scripts/lib/synthesize.sh` (or wherever the translator code lives) for INBOX deposit logic.
- Look for any existing slug-prefix deduplication or suppression logic.
- If suppression enforcement is already in place, verify it:
  - Counts existing INBOX items by slug-prefix before deposit
  - Suppresses new items when count ≥5
  - Logs suppression detail in the synthesis output
- If already implemented, write completion report stating "already landed and verified".

## Acceptance criteria

If not already landed:
- Translator code (in synthesize.sh or equivalent) includes logic:
  ```
  if (count_existing_inbox_items_with_prefix(proposal_slug) >= 5) {
    log_suppression_in_synthesis_output(proposal_slug, count)
    skip_handoff_deposit()
  } else {
    deposit_handoff_to_inbox()
  }
  ```
- The suppression is logged in the synthesis output under a "Suppressed proposals" or similar section.
- Existing INBOX items are not affected — only new deposits are gated.
- Commit message: "Enforce INBOX suppression rule in synthesis translator — suppress new proposals when theme ≥5 items"
- Completion report at `runtime/.handoff/general-complete-inbox-suppression-enforcement-<iso>.md`

## Escalation

If translator code location is different than expected, escalate with the actual path. If the rule is more complex than described, surface the specifics.
