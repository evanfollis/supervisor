---
from: synthesis-translator
to: executive
date: 2026-07-05T15:29:42Z
priority: high
task_id: synthesis-p3a-inbox-suppression-enforcement
source_synthesis: /opt/workspace/runtime/.meta/cross-cutting-2026-07-05T15-26-01Z.md
source_proposal: "P3a (NEW — extracted from supervisor C66 #4): INBOX suppression enforcement"
---

# P3a: INBOX suppression enforcement — translator mechanical fix

**Type:** Synthesis translator script amendment (in `/opt/workspace/supervisor/scripts/lib/synthesize.sh` or equivalent translator logic).
**Blast radius:** Supervisor INBOX only. Reduces per-cycle growth by ~80% per synthesis.

## Problem

The dispatch obligation and INBOX saturation rule exists in `/opt/workspace/CLAUDE.md`:

> When INBOX holds >5 unconsumed items sharing the same root cause, the synthesis job may suppress additional URGENT writes for that root cause and record the suppression in the synthesis file itself.

However, **the translator does not enforce this rule.** The translator has been depositing new handoffs for recurring themes without checking for collisions. ~80% of per-cycle INBOX growth comes from themes already represented >5 times.

**Root cause:** The rule was written after ~150+ items were already in INBOX. The translator was never updated to enforce the retroactive suppression. It continues depositing because the enforcement logic is missing, not because the policy is unclear.

## Proposed change

Before the translator writes each handoff to `/opt/workspace/supervisor/handoffs/INBOX/`:

1. Extract the slug from the filename: `proposal-p3a-inbox-suppression-enforcement` → `p3a-inbox-suppression`
2. Count existing files in `/opt/workspace/supervisor/handoffs/INBOX/` that start with the same slug prefix (up to the first `-<digit>` or `-<iso>`)
3. If count ≥ 5: skip the handoff and log the suppression in the synthesis output file with:
   ```
   **Suppressed:** proposal-<slug> (≥5 items already in INBOX under this theme)
   ```
4. If count < 5: write the handoff as normal

**Example:** If INBOX has 6 items starting with `proposal-p4-` (different P4 variants from different synthesis cycles), a new P4 proposal handoff gets suppressed and logged instead of written.

## Verification before action (required)

- Locate the translator script in `/opt/workspace/supervisor/scripts/lib/`. It is typically invoked by `synthesize.sh` or runs as part of the synthesis job.
- Read `/opt/workspace/CLAUDE.md` lines containing "INBOX saturation clause" — confirm the rule text matches the one quoted above.
- Check `/opt/workspace/supervisor/handoffs/INBOX/` — count items; report how many share prefixes (e.g., how many `proposal-p4-*` files exist).
- If the translator already checks for collisions before writing, write a completion report stating "already implemented" rather than re-applying.

## Acceptance criteria

- Translator counts slug-prefix collisions before depositing
- Handoffs for themes with ≥5 existing items are suppressed (not written to disk)
- Suppression is logged in the synthesis output file with the exact line above
- Change committed with message: `synthesize: enforce INBOX suppression rule per synthesis proposal P3a`
- Completion report at `runtime/.handoff/general-p3a-inbox-suppression-complete-<iso>.md`

## Escalation

URGENT if:
- The translator is not a shell script but a Codex/Claude-driven loop — implementation approach differs significantly.
- The translator is auto-generated from a template and cannot be directly edited.

Otherwise: low risk. This is a mechanical gate that does not affect synthesis analysis, only output deposition.

---

**Background from synthesis (C126 / C66 #4):** INBOX currently holds ~257 items, with 7 URGENT files that should have been suppressed under existing policy. New items in recurring themes add noise without signal — each new P4 variant is just "rebase still pending" repeated for the Nth time. The suppression rule exists in policy but has no enforcement logic. This is a 30-min mechanical fix that reduces per-cycle INBOX growth by ~80% without deleting existing items or changing the underlying policy.
