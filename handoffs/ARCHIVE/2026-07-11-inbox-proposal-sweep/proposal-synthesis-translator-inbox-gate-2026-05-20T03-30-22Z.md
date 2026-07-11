---
from: synthesis-translator
to: general
date: 2026-05-20T03:30:22Z
priority: high
task_id: synthesis-translator-inbox-gate
source_synthesis: /opt/workspace/runtime/.meta/cross-cutting-2026-05-20T03-25-45Z.md
source_proposal: "Proposal 2 (HIGH — 9th cycle): Gate synthesis-translator on INBOX count"
---

# Gate synthesis-translator on INBOX count

## Context

The synthesis-translator job deposits 3–5 new proposal files every cycle. INBOX has grown to 40 items (verified 2026-05-20T03:25Z). The carry-forward escalation gate and the INBOX saturation suppression form a logical deadlock: items that should escalate to INBOX cannot because INBOX is full, and INBOX stays full because no attended session processes it.

The translator needs a gate that pauses handoff emission when INBOX is already saturated, to prevent the output queue from becoming noise.

## The Fix

**File**: `supervisor/scripts/lib/synthesis-translator.sh`
**Target**: Add an INBOX count check before depositing handoffs

Pseudo-code:
```bash
# At the top of the main handoff-emission loop:
INBOX_COUNT=$(find "$INBOX_DIR" -type f -name "*.md" 2>/dev/null | wc -l)
MAX_INBOX_BEFORE_GATE=40  # Configurable; current INBOX is at this threshold

if [[ "$INBOX_COUNT" -ge "$MAX_INBOX_BEFORE_GATE" ]]; then
  # INBOX is already saturated; do not deposit more proposals
  echo "synthesis-translator: INBOX at $INBOX_COUNT items (>= $MAX_INBOX_BEFORE_GATE); suppressing proposal deposits" >> "$LOG_FILE"
  exit 0  # Clean exit; synthesis itself succeeded, translation is just gated
fi
```

The gate should:
- Count `.md` files in `/opt/workspace/supervisor/handoffs/INBOX/`
- Suppress ALL handoff writes (both INBOX and `runtime/.handoff/`) if count is >= threshold
- Log the suppression with the count and reason
- Exit cleanly (this is not a failure; it is intentional backpressure)
- Emit an event `{ "type": "translation_gated_inbox_saturation", "inbox_count": N, ... }` if telemetry exists

## Blast Radius

- Synthesis-translator only (automatic, no project code affected)
- Prevents INBOX from growing unbounded while already sat urated
- Allows synthesis output to exist (the synthesis file itself still lands) without forcing handoff deposits that become noise

## Cycles open

- 9 cycles as synthesis proposal
- 8 consecutive prediction confirmations of 3–5 deposits per cycle

## Verification before action (required)

- Verify `synthesis-translator.sh` exists and is executable at `/opt/workspace/supervisor/scripts/lib/synthesis-translator.sh`
- Confirm no prior INBOX gate logic exists: `grep -c INBOX_COUNT synthesis-translator.sh` should be 0
- Confirm `/opt/workspace/supervisor/handoffs/INBOX/` directory exists
- If any checks fail, escalate with the specific gap named.

## Acceptance criteria

- A gate function or conditional is added that counts items in `INBOX_DIR` before emission
- Gate threshold is configurable (recommend 40 as current saturation point)
- When gate is triggered, no handoff files are written
- Suppression is logged with count and reason
- Telemetry event is emitted if available
- Change committed with message explaining the gate and its rationale
- Completion report at `runtime/.handoff/general-supervisor-synthesis-translator-inbox-gate-complete-<iso>.md`

## Escalation

URGENT if:
- The gate is already implemented (committed by another path between synthesis and now)
- Implementing the gate requires hardcoding INBOX path or threshold in a way that breaks if config changes
- The gate would require principal decision on when/how to handle saturated INBOX
