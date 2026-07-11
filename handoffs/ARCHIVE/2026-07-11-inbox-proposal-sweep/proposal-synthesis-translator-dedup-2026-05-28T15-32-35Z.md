---
from: synthesis-translator
to: general
date: 2026-05-28T15:32:35Z
priority: high
task_id: synthesis-translator-cross-cycle-dedup
source_synthesis: /opt/workspace/runtime/.meta/cross-cutting-2026-05-28T15-26-51Z.md
source_proposal: P7 — Cross-cycle dedup in synthesis-translator
---

# Cross-cycle dedup in synthesis-translator

## Problem

The synthesis-translator emits one handoff file per proposal per synthesis cycle. Filenames include a per-cycle timestamp, so the idempotency check (line 95 of `synthesis-translator-prompt.md`) only prevents re-runs of the *same* synthesis. Across cycles, identical proposals are re-deposited, creating duplicate files in INBOX.

**Current impact:** INBOX holds 101 proposal files spanning May 8–28, representing ~79 distinct proposal stems with ~22 cross-cycle duplicates. At 2 synthesis cycles/day × 3–6 proposals/cycle, the translator deposits 6–12 files daily into a queue with zero consumption over 20+ days. Within 10 days, INBOX will hold ~200 proposal files; the triage cost defeats the translator's purpose.

## Proposed fix

Modify `/opt/workspace/supervisor/scripts/lib/synthesis-translator-prompt.md` to add a cross-cycle dedup check before emitting proposal handoffs.

**Add to §2 ("For each proposal, decide:") after the principal-scope check:**

```markdown
3. **Cross-cycle dedup check:**
   - Before writing a handoff, run: `ls {{INBOX_DIR}}/proposal-<slug>-*.md 2>/dev/null`
   - If any match exists, read the most recent file.
   - If the proposal body is substantively unchanged, skip with:
     ```
     Skipped (cross-cycle duplicate): proposal-<slug> already in INBOX from <date>
     ```
   - If the proposal has materially changed (new rationale, updated scope, or different acceptance criteria), overwrite the newest match rather than creating a new file. This preserves history while preventing duplicates.
```

**Update the "2. For each proposal, decide:" section to include this check as step 3.**

## Why

The translator was designed to close the diagnosis→execution gap. Without cross-cycle dedup, it instead converts each synthesis cycle's proposals into cumulative queue pollution. The 101 files are now a larger triage surface than the 15 dead-letter maintenance handoffs and 7 runtime URGENTs combined.

This fix prevents further accumulation. The existing 101 files still need a one-time cleanup pass in the first attended session (bulk-archive files older than 48h whose stem has a newer duplicate).

## Verification before action (required)

- Check `/opt/workspace/supervisor/scripts/lib/synthesis-translator-prompt.md` to confirm the idempotency check is present at line 95 (or nearby).
- Verify the current format uses `{{ISO_FILENAME}}` in the filename template, which includes a per-cycle timestamp.
- If the translator has already been modified to include cross-cycle dedup, write a completion report stating "already landed" with the commit SHA.

## Acceptance criteria

- The cross-cycle dedup check is added to §2 of the translator prompt, before the "Otherwise: it is autonomous-bucket work" line.
- The check uses glob matching on `proposal-<slug>-*.md` to find prior deposits.
- The check reads the most recent match and compares proposal body for substantive changes.
- Unchanged proposals are skipped with a clear "cross-cycle duplicate" note.
- Changed proposals are overwritten (one file per stem, most recent version).
- The translator's report section is updated to include "Skipped (cross-cycle duplicate): N proposals" in the count.
- No adversarial review required (prompt/config change, not code logic change).
- Completion report at `/opt/workspace/supervisor/handoffs/INBOX/general-synthesis-dedup-complete-<iso>.md` points back to this handoff and the source synthesis.

## Escalation

URGENT if:
- The translator has already been updated cross-cycle dedup. If so, state the commit and close the handoff as obsolete.
- The INBOX directory structure has changed since the synthesis run, making the glob path invalid. Verify the INBOX path matches `{{INBOX_DIR}}` in the translator template.
