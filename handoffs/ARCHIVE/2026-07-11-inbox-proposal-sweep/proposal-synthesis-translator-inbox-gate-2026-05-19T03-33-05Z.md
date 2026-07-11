---
from: synthesis-translator
to: general
date: 2026-05-19T03:33:05Z
priority: high
task_id: synthesis-translator-inbox-gate
source_synthesis: /opt/workspace/runtime/.meta/cross-cutting-2026-05-19T03-25-36Z.md
source_proposal: Proposal 2 (CARRIED from cycle 39, 7th cycle) — Gate synthesis-translator on INBOX count
---

# Proposal 2: Gate synthesis-translator on INBOX count

## Background

INBOX has grown from 29 to 33 items (4 translator deposits from cycle 44, zero consumption). The synthesis-translator has no count gate and will deposit 3–5 new proposals from this synthesis, pushing INBOX to 36–38. The prediction has been correct for 6 consecutive cycles. This is the mechanical fix to suppress deposits when INBOX is saturated.

## Implementation

Add the following check to `/opt/workspace/supervisor/scripts/lib/synthesis-translator.sh` **before the main proposal-extraction loop**:

```bash
# Gate: suppress deposits if INBOX is already saturated
INBOX_COUNT=$(find "$INBOX_DIR" -name '*.md' 2>/dev/null | grep -v .gitkeep | wc -l)
if [ "$INBOX_COUNT" -gt 10 ]; then
  echo "[synthesis-translator] INBOX at $INBOX_COUNT (>10); deposit suppressed per saturation exception" >&2
  exit 0
fi
```

**Location hint:** This check should be placed in the `synthesis-translator.sh` script, likely just before the section that starts reading and parsing proposals from the synthesis file. The check should use `$INBOX_DIR` (already defined in the script around line 42-43).

## Verification before action (required)

- Confirm current INBOX count: `ls /opt/workspace/supervisor/handoffs/INBOX/ | grep -v .gitkeep | wc -l` — verify it is 33 (or count at time of action)
- Confirm the gate threshold is appropriate: `grep -n "INBOX_COUNT" /opt/workspace/supervisor/scripts/lib/synthesis-translator.sh` — verify it does not already exist
- Test the gate works: add temporary `echo` statements to verify the condition is evaluated correctly on the next synthesis run

## Acceptance criteria

- The gate code is added to synthesis-translator.sh
- Gate uses the existing `$INBOX_DIR` variable (defined ~line 42-43)
- The threshold is 10 items; adjust only with explicit principal decision
- On the next synthesis run (cycle 46, ~03:25Z), INBOX does not grow beyond 33 (gate suppresses translator deposits)
- Change committed with message "synthesis-translator: gate deposits on INBOX count >10"
- Completion report confirms the gate suppressed deposits on cycle 46

## Escalation

URGENT if:
- The gate blocks deposits indefinitely (INBOX never decreases below threshold) — this indicates the root issue is queue consumption, not deposit velocity
- The next attended session indicates the proposal count from this synthesis is critical and should not be suppressed — escalate the gate threshold decision to the principal
