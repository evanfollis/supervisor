---
from: synthesis-translator
to: general
date: 2026-05-15T15:27:59Z
priority: high
task_id: synthesis-inbox-count-gate
source_synthesis: /opt/workspace/runtime/.meta/cross-cutting-2026-05-15T15-23-27Z.md
source_proposal: Proposal 2 — INBOX count gate in tick dispatcher
---

# INBOX count gate in tick dispatcher

**Type:** Shared primitive change — `supervisor-tick.sh`.

**Carried from:** Cycle 37 (honor-system rule stated); now with mechanical sketch after second consecutive violation.

## Problem statement

The honor-system deposit-pause rule ("no new INBOX files when INBOX >10 and consumption is 0 for 3+ cycles") has failed to enforce itself for two consecutive cycles:

- **Cycle 37:** The synthesis that proposed the rule was violated in the same cycle that proposed it. Synthesis translator deposited 3 items (03:30Z); the 04:48Z tick deposited more. INBOX grew from 18 → 21.
- **Cycle 38:** The 04:48Z tick deposited 3 new INBOX items, growing the queue from 18 → 21. The rule is partially adopted when ticks read the synthesis output; it fails when they don't, and it fails structurally in the synthesis-translator (which deposits proposals before the pause rule can be applied).

**Current state:** INBOX at 21 items (4 URGENTs + 17 proposals). Consumption rate: 0 for 4+ synthesis cycles.

**Underlying failure class:** Honor-system rules in automated pipelines. The rule is stated in prose; the dispatcher is a shell script that doesn't read prose. Without a mechanical gate (check INBOX count before write), every new synthesis cycle and tick will continue depositing.

## Implementation

**5-line sketch:**

```bash
INBOX_COUNT=$(ls supervisor/handoffs/INBOX/*.md 2>/dev/null | wc -l)
if [ "$INBOX_COUNT" -gt 10 ]; then
  echo "[SUPPRESSED] INBOX at $INBOX_COUNT items; deposit paused" >> "$TICK_LOG"
  return 0  # skip INBOX write
fi
```

**Scope:** Supervisor tick dispatcher + synthesis translator (automatic). Prevents INBOX growth past 10 until consumption occurs.

## Verification before action (required)

- Run `git log --oneline -20` in `/opt/workspace/supervisor`. Check if this INBOX gate has already landed via another path.
- Read `/opt/workspace/supervisor/scripts/lib/supervisor-tick.sh`. Check if INBOX count checks are already present before `friction_filed` or INBOX-write blocks.
- If either is true, write a completion report stating "already landed at commit <SHA> / verified in-file" rather than re-applying.

## Acceptance criteria

- INBOX count gate is implemented in supervisor-tick.sh dispatcher
- Before any new INBOX file write, the gate checks `ls supervisor/handoffs/INBOX/*.md | wc -l`
- When INBOX count > 10, the dispatcher logs suppression and skips the write
- Change committed with clear message: "Add mechanical INBOX count gate to prevent unbounded growth"
- No adversarial review required (focused code fix, minimal scope)
- Completion report at `runtime/.handoff/general-supervisor-synthesis-inbox-count-gate-complete-<iso>.md` pointing back to this handoff and the source synthesis

## Notes

- This gate applies to all INBOX deposits: tick-generated friction files, synthesis proposals, and translator proposals
- The synthesis translator uses the same gate when it writes Proposal 1 and Proposal 3 handoffs (same cycle)
- Once INBOX drops below 10 and consumption resumes, deposits automatically resume

## Escalation

URGENT if:
- Primary verification reveals this has already landed. Close with "obsolete — already landed."
- The gate is implemented but INBOX continues growing past 10. Verify the gate is executing and check supervisor tick logs.
