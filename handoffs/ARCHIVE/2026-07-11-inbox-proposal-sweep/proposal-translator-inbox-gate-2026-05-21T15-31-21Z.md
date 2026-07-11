---
from: synthesis-translator
to: general
date: 2026-05-21T15:31:21Z
priority: high
task_id: synthesis-translator-inbox-gate
source_synthesis: /opt/workspace/runtime/.meta/cross-cutting-2026-05-21T15-24-47Z.md
source_proposal: "Proposal 2 (HIGH — 12th cycle): Gate synthesis-translator on INBOX count"
---

# Gate synthesis-translator on INBOX count

**Type:** Shared primitive fix.

**Blast radius:** Synthesis-translator only (automatic, no impact on other systems).

**Current state (VERIFIED):** 
- `grep -c 'INBOX_COUNT' /opt/workspace/supervisor/scripts/lib/synthesis-translator.sh` → 0
- Translator deposits handoffs to INBOX unconditionally, regardless of INBOX saturation state
- Per CLAUDE.md saturation exception, synthesis suppresses internal URGENTs when INBOX > 5 items, but translator still deposits

**Problem:** The translator continues depositing handoffs to INBOX even when saturation suppression is active. This creates a pathological loop:
1. INBOX fills beyond 5 items
2. Synthesis suppresses URGENT deposits to avoid adding noise to a saturated queue
3. Translator runs and deposits handoffs anyway, defeating the saturation suppression
4. INBOX stays saturated

This has repeated for 11 consecutive cycles (confirmed at 15:24Z today). INBOX is currently at **53 items**.

**Prediction (from synthesis):** "Translator will deposit after this synthesis, pushing INBOX to 56–59. Confirmed 11 consecutive cycles."

**Fix:** Modify `/opt/workspace/supervisor/scripts/lib/synthesis-translator.sh` to check INBOX item count before depositing handoffs:

```bash
# Near the top of the translator, after sourcing variables:
INBOX_COUNT=$(ls "$INBOX_DIR" 2>/dev/null | wc -l)
INBOX_THRESHOLD=5  # or appropriate limit per CLAUDE.md saturation exception

# After processing all proposals, before emitting handoffs:
if [[ "$INBOX_COUNT" -ge "$INBOX_THRESHOLD" ]]; then
  echo "synthesis-translator: INBOX at $INBOX_COUNT items (threshold $INBOX_THRESHOLD); suppressing deposits per saturation policy" >&2
  # Do not write any handoff files; skip the deposit phase
  exit 0
fi
```

Alternatively: emit handoffs to a staging directory and signal the supervisor that deposits are queued but suppressed. The simplest fix is to exit early without depositing.

## Verification before action (required)

- ✓ Checked synthesis-translator.sh for existing INBOX gate — none found
- ✓ Confirmed INBOX saturation suppression is active in synthesis (line 158)
- ✓ Confirmed 11-cycle pattern of translator deposits despite saturation (line 160)
- This fix is a straightforward guard clause with no side effects on other synthesis behavior

## Acceptance criteria

- Translator checks `ls INBOX/ | wc -l` before depositing handoffs
- Translator skips deposit phase (does not create .md files) when INBOX count exceeds threshold
- Translator emits a log message indicating suppression and the INBOX count
- No handoffs are written when suppression is active
- Change committed with message: "Gate synthesis-translator deposits on INBOX saturation count"

## Escalation

None anticipated. This is a straightforward guard clause that honors CLAUDE.md saturation policy. The synthesis job has already committed to suppressing URGENTs; the translator must honor the same gate to avoid defeating the suppression.
