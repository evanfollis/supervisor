---
from: synthesis-translator
to: general
date: 2026-05-24T15:32:58Z
priority: high
task_id: synthesis-tick-promote-questions
source_synthesis: /opt/workspace/runtime/.meta/cross-cutting-2026-05-24T15-26-05Z.md
source_proposal: Proposal 1 — Tick must promote synthesis "Questions for the human" to active-issues "Pending principal"
---

# Proposal 1: Tick must promote synthesis "Questions for the human" to active-issues "Pending principal"

**Pattern 1 diagnosis**: Cycle-55 synthesis included two explicit "Questions for the human" — Q1 (repair-before-strategy ordering) and Q2 (adversarial review route decision). The 04:47Z tick consumed this synthesis content but did NOT:

- emit `escalated` events for either question
- promote either question to `system/active-issues.md` "Pending principal" section

The "Pending principal" section is the only surface the principal actually reads for decision items. If the tick reads synthesis questions but doesn't promote them to that section, the principal never sees them. The synthesis loop becomes diagnosis → proposal → question → silence, not because the principal ignores the question but because the question never reaches the principal's reading surface.

**Type:** Shared primitive fix (`supervisor-tick.sh`).

**What:** After the tick reads a synthesis file, if the file contains a `## Questions for the human` section, each question must be:
  - (a) appended to `system/active-issues.md` "Pending principal" section (if not already present — dedup by content substring match)
  - (b) emitted as an `escalated` event in `supervisor-events.jsonl`

**Why:** Cycle-55 Q1 and Q2 never reached the principal because the tick absorbed the synthesis observations but did not promote the questions. This is the structural cause of the "synthesis produces questions → no response" failure pattern. Without this fix, the entire synthesis → question → principal pipeline has zero delivery guarantee.

**Blast radius:** Supervisor tick only (automatic). Affects `system/active-issues.md` and `supervisor-events.jsonl`. All projects benefit indirectly because synthesis questions about workspace-wide issues (reflect.sh, review gate) will reach the principal's reading surface.

**Reference implementation sketch:**
```bash
# In supervisor-tick.sh, after reading LATEST_SYNTHESIS:
if grep -q '^## Questions for the human' "$SYNTHESIS_FILE"; then
  # Extract questions, dedup against active-issues, append to Pending principal
  questions=$(sed -n '/^## Questions for the human/,/^## /p' "$SYNTHESIS_FILE" | grep -E '^\d+\.')
  while IFS= read -r q; do
    # Only add if not already present (substring match)
    if ! grep -qF "${q:0:60}" system/active-issues.md; then
      sed -i "/^## Pending principal/a - **[Cycle ${CYCLE_NUM}]** ${q}" system/active-issues.md
    fi
  done <<< "$questions"
  # Emit escalated event
  _emit_event "escalated" "synthesis-questions-cycle-${CYCLE_NUM}" \
    "Promoted $(echo "$questions" | wc -l) synthesis questions to active-issues Pending principal"
fi
```

## Verification before action (required)

- [ ] Check if this has already landed in `supervisor/scripts/lib/supervisor-tick.sh` by searching for `Questions for the human` promotion logic. If present, write completion report "already landed" with the commit hash.
- [ ] If not landed: read current state of `supervisor/scripts/lib/supervisor-tick.sh` to understand where the new code should be inserted (after LATEST_SYNTHESIS is read, before the report is written).

## Acceptance criteria

- The implementation detects `## Questions for the human` sections in synthesis files.
- Each question is appended to `system/active-issues.md` "Pending principal" section with a `[Cycle N]` prefix.
- Deduplication prevents duplicate questions from being added on re-runs of the same synthesis.
- An `escalated` event is emitted to `supervisor-events.jsonl` for each synthesis that contains questions.
- Change is committed with clear message: "Fix: promote synthesis questions to active-issues Pending principal section"
- No adversarial review needed for this fix (it is a straightforward logic addition that improves the delivery pipeline).

## Escalation

URGENT if:
- The proposal has already landed in the current supervisor-tick.sh via another path. Write a completion report: "already landed at commit <SHA>" and close.
- The supervisor-tick.sh structure has changed significantly from the sketch, making the insertion point unclear. Escalate with the current file structure so principal can clarify intent.
