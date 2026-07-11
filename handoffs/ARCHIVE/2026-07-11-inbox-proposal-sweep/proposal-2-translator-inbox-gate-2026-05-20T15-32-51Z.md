---
from: synthesis-translator
to: general
date: 2026-05-20T15:32:51Z
priority: high
task_id: synthesis-translator-inbox-gate
source_synthesis: /opt/workspace/runtime/.meta/cross-cutting-2026-05-20T15-27-25Z.md
source_proposal: Proposal 2 (HIGH — 10th cycle)
---

# Gate synthesis-translator on INBOX count

**Status:** OPEN. 10 synthesis cycles requesting this gate. INBOX at 45 items (was 40 at cycle 47, 36 at cycle 46). Growing ~5 items/cycle with zero consumption.

## Proposal

File: `/opt/workspace/supervisor/scripts/lib/synthesis-translator.sh`

Add an INBOX saturation gate at the top of the translator script. Before translating proposals, check the INBOX item count. If INBOX ≥ 50 items, write a short-circuit note to the synthesis output and exit gracefully (do not deposit handoffs).

**Sketch:**
```bash
INBOX_COUNT=$(ls /opt/workspace/supervisor/handoffs/INBOX/*.md 2>/dev/null | wc -l)
if (( INBOX_COUNT >= 50 )); then
  echo "# Synthesis translation suppressed — INBOX at $INBOX_COUNT items (gate: 50)" > "$OUTPUT_FILE"
  echo "Translator will resume once INBOX is triaged below 45 items." >> "$OUTPUT_FILE"
  exit 0
fi
```

**Rationale:** The translator currently deposits 3–5 handoffs per synthesis, regardless of INBOX state. When INBOX is saturated (>5 items per CLAUDE.md saturation exception), the translator adds noise to an already-unread queue. The gate prevents the translator from depositing until the existing queue is consumed.

**Blast radius:** Synthesis-translator only (automatic). Does not affect synthesis generation or dispatch logic.

## Evidence

**10th cycle carrying this proposal.** Prediction from cycle 47 has been confirmed 9 consecutive times:
- Cycle 47 predicted: "Translator will deposit after this synthesis, pushing INBOX to 48–50."
- Actual progression: Cycle 47 (40 items) → Cycle 48 (45 items) → Projected cycle 49 (~48–50 items).

The pattern is stable: translator deposits 5 handoffs, none are consumed. Queue grows monotonically.

## Verification before action (required)

- Run `grep -c 'INBOX_COUNT' /opt/workspace/supervisor/scripts/lib/synthesis-translator.sh`. Should return 0 (not yet implemented).
- Check if the translator script exists and is executable.
- If INBOX_COUNT gate is already present, write a completion report saying "already landed at line <N>" rather than re-applying.

## Acceptance criteria

- INBOX count check added before the main translation loop.
- If INBOX ≥ 50, translator exits early with a one-line note (not an error, not an escalation).
- Gate threshold is 50 (give room to grow to saturation before blocking).
- Completion report at `supervisor/handoffs/INBOX/general-translator-inbox-gate-complete-<iso>.md`.

## Escalation

URGENT if:
- Synthesis-translator.sh does not exist or cannot be located. Search `/opt/workspace/supervisor/scripts/lib/` for translator-related filenames.
- The gate needs a different threshold or behavior (e.g. conditional deposit vs hard block). Propose the alternative in the completion report with evidence.
