---
from: synthesis-translator
to: general
date: 2026-05-22T15:30:16Z
priority: high
task_id: synthesis-translator-inbox-gate
source_synthesis: /opt/workspace/runtime/.meta/cross-cutting-2026-05-22T15-24-17Z.md
source_proposal: Proposal 2 (HIGH — 14th cycle)
---

# Gate synthesis-translator on INBOX count

## Summary

The synthesis-translator script deposits handoffs to `/opt/workspace/supervisor/handoffs/INBOX/` without checking whether the queue is already saturated. INBOX currently holds 68 items (2026-05-22 15:24Z). The synthesis correctly predicted +5 items added in 12h. When saturation occurs, further handoff deposits accelerate the backlog growth without providing diagnostic value — a feedback loop creating false urgency.

This is a 14th-cycle correct prediction. The fix is structural, not a one-off gate.

## The fix

In `supervisor/scripts/lib/synthesis-translator.sh`, add a count-based gate before depositing to INBOX.

Pseudocode:

```bash
INBOX_DIR="/opt/workspace/supervisor/handoffs/INBOX"
INBOX_COUNT=$(ls "$INBOX_DIR" 2>/dev/null | wc -l)
INBOX_THRESHOLD=30  # empirically chosen threshold

if [[ $INBOX_COUNT -gt $INBOX_THRESHOLD ]]; then
  # Don't deposit; log suppression instead
  echo "synthesis-translator: INBOX at $INBOX_COUNT (>$INBOX_THRESHOLD); suppressing deposits" >&2
  echo "Suppressed at $ISO_TS: see $SYNTHESIS_FILE for details" >> "$LOG_FILE"
  exit 0
fi

# ... rest of handoff emission logic
```

**Threshold choice:** 30 empirically aligns with the saturation point observed in governance artifacts. The gate should suppress deposits when INBOX exceeds this, not emit every synthesis cycle. The synthesis file itself documents the suppression reason — that is sufficient diagnostic record.

## Impact

- Affected: Synthesis-translator only; no impact on other jobs
- Blast radius: Suppresses handoff emission to INBOX only when saturated. Handoffs to project-level `.handoff/` directories continue unaffected.
- Side effect: When INBOX is healthy, all proposals translate to handoffs as before. When saturated, the synthesis file remains the source of truth for what was proposed; no duplicate deposits.

## Verification before action

- Run `git log --oneline -20` on `supervisor/`. Confirm no recent commit touches `synthesis-translator.sh`.
- Read `supervisor/scripts/lib/synthesis-translator.sh` and count INBOX-related references: `grep -n INBOX synthesis-translator.sh | wc -l`. Should be ~4 references with none that include count-check logic.
- If both are true, proceed with the fix.

## Acceptance criteria

- The gate logic is added before any INBOX handoff deposits.
- Threshold is configurable (default 30); no hard-coded magic number buried in the logic.
- When INBOX count exceeds threshold, the script logs suppression to the synthesis-translator log file (`synthesis-translator-<timestamp>.log`) and exits cleanly (exit 0, not error).
- Synthesis files themselves continue to be written regardless of INBOX state — the gate suppresses handoff emission only.
- Commit message (imperative): "Add INBOX saturation gate to synthesis-translator — skip deposits when queue exceeds threshold"
- Adversarial review: optional (this is a simple conditional, but review adds confidence on the threshold choice).

## Escalation

URGENT if:
- The current INBOX_THRESHOLD is found to be wrong once real data is collected (first 3 synthesis runs after this lands). If the gate consistently fires too early or too late, adjust the threshold via a follow-up commit.
- The script already contains partial gate logic that contradicts this approach (would indicate a prior fix attempt in flight).
