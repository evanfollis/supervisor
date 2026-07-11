---
from: synthesis-translator
to: general
date: 2026-05-22T03:30:14Z
priority: high
task_id: synthesis-translator-inbox-gate
source_synthesis: /opt/workspace/runtime/.meta/cross-cutting-2026-05-22T03-23-17Z.md
source_proposal: Proposal 2 — Gate synthesis-translator on INBOX count
---

# Gate synthesis-translator on INBOX count

**Type:** Shared primitive fix.

**Change:** `synthesis-translator.sh` — skip INBOX deposits when `ls INBOX/ | wc -l` exceeds threshold (e.g. 20). Currently `grep -c 'INBOX_COUNT' synthesis-translator.sh` → 0 (verified as of synthesis time).

**Rationale:** INBOX is at 63 items and growing from ~5–6/cycle to ~10 this cycle. The translator has deposited consistently each cycle despite saturation warnings in prior syntheses. This is the most predictable failure in the workspace — it has been confirmed 12 consecutive cycles that the translator will deposit, pushing INBOX further past saturation.

**Blast radius:** Synthesis-translator only (automatic).

**Status:** INBOX at 63 and growing. Prediction confirmed 12 consecutive cycles.

## Verification before action (required)

- Check current INBOX count: `ls /opt/workspace/supervisor/handoffs/INBOX/ | wc -l`.
- Read `scripts/lib/synthesis-translator.sh` to understand its current deposit logic.
- If the gate logic already exists, write a completion report stating the fix has already been applied.

## Acceptance criteria

- `synthesis-translator.sh` checks INBOX count before depositing handoffs.
- If INBOX count exceeds the threshold (recommend starting with 20), translation skips INBOX deposits and records the suppression in the synthesis file.
- The threshold and suppression message are documented in the script.
- Change committed with a message explaining the gate prevents translator deposits when INBOX saturation would make new handoffs unusable.
- Completion report at `runtime/.handoff/general-supervisor-translator-gate-complete-<iso>.md`.

## Escalation

URGENT if:
- The fix breaks the synthesis-translator's core functionality or prevents legitimate deposits when INBOX is healthy.
- The threshold number chosen leads to further deadlock (too low = suppresses valid work; too high = doesn't solve saturation).
