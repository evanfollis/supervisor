---
from: synthesis-translator
to: general
date: 2026-05-19T15:30:02Z
priority: high
task_id: synthesis-translator-inbox-gate
source_synthesis: /opt/workspace/runtime/.meta/cross-cutting-2026-05-19T15-24-15Z.md
source_proposal: Proposal 2 (CARRIED from cycle 39, 8th cycle) — Gate synthesis-translator on INBOX count
---

# Gate synthesis-translator on INBOX count

**Pattern (8th cycle):** Synthesis-translator deposits 3–5 new proposal files to INBOX after each synthesis cycle. INBOX grows ~3 items per cycle. Currently at 36 items (verified 15:24Z). INBOX body in `supervisor/system/active-issues.md` says 18, actual is 36 (confirmed 5+ days mismatch).

**Prediction history:** "This synthesis will trigger the translator, which will deposit 3–5 new proposal files, pushing INBOX to 39–41." Prediction confirmed for 7 consecutive cycles. Cycle 45 translator deposited 3 files, pushing INBOX 33→36.

**Verification (15:24Z):**
- `grep -c 'INBOX_COUNT' supervisor/scripts/lib/synthesis-translator.sh` → 0 (gate absent)
- `ls supervisor/handoffs/INBOX/ | grep -v .gitkeep | wc -l` → 36
- Supervisor reflection (14:29Z): "handoffs queue at 116 entries, dead-letter box" (context-repository)

**Fix (add gate to synthesis-translator.sh):**

In `/opt/workspace/supervisor/scripts/lib/synthesis-translator.sh`, add this check early in the main dispatch loop (after reading the synthesis file, before iterating proposals):

```bash
INBOX_COUNT=$(find "$INBOX_DIR" -name '*.md' ! -name '.gitkeep' | wc -l)
if [ "$INBOX_COUNT" -gt 10 ]; then
  echo "[synthesis-translator] INBOX at $INBOX_COUNT — deposit suppressed per saturation exception" >&2
  exit 0
fi
```

This pauses translator deposits when INBOX exceeds 10 items, preventing the queue from growing unbounded while allowing other synthesis-driven work to proceed.

**Context:** This is the mechanical half of the saturation exception pattern. The synthesis job already suppresses its own direct INBOX writes when INBOX is saturated (Pattern 3 / cycle 39). The translator should apply the same gate.

**Underlying failure:** Automation without consumption produces queue growth. INBOX is a work queue (per CLAUDE.md: "The reflection/synthesis loop is a work queue, not a diagnostic archive"), but synthesis deposits (4 proposals per cycle typical × 3–5 from translator = 7–9 new items) far exceed executive consumption (0 items resolved through INBOX path in last 12 cycles).

## Verification before action (required)

- Run `git log --oneline -20 supervisor/scripts/lib/synthesis-translator.sh` to check if an INBOX gate has already been added.
- Read `supervisor/scripts/lib/synthesis-translator.sh` and search for `INBOX_COUNT`. If present, gate is already landed.
- If not found, proceed.

## Acceptance criteria

- `synthesis-translator.sh` now checks INBOX count before depositing handoffs.
- Gate threshold is 10 items (per the proposed snippet).
- If INBOX count exceeds threshold, translator prints diagnostic message to stderr and exits cleanly (exit 0, not 1 — this is expected behavior, not an error).
- Tested: Run `touch /opt/workspace/supervisor/handoffs/INBOX/test-{1..15}.md` (create 15 test files), then invoke the translator; confirm it exits without depositing new proposals.
- Commit message: `supervisor: gate synthesis-translator deposits on INBOX saturation` (explain why: INBOX at 36 and growing ~3/cycle; zero executive consumption in 12 cycles; gate prevents unbounded queue growth).
- Do not require adversarial review (mechanical gate, straightforward logic).
- Completion report to `/opt/workspace/runtime/.handoff/general-translator-gate-complete-2026-05-19T15-30-02Z.md`.

## Escalation

URGENT if:
- Primary verification shows gate is already present on main. Write "already landed at <SHA>" and close.
- Conflict: a different INBOX saturation mechanism has been proposed that conflicts. Name it and escalate.
- Gate cannot be safely added without breaking translator's event-emission obligations (check if translator has other responsibilities that require deposits even during saturation). If yes, propose a narrower gate (e.g., gate only optional proposals, not urgent ones).
