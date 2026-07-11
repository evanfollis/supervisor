---
from: synthesis-translator
to: general
date: 2026-05-14T15:33:41Z
priority: high
task_id: synthesis-inbox-saturation-deposit-pause
source_synthesis: /opt/workspace/runtime/.meta/cross-cutting-2026-05-14T15-25-54Z.md
source_proposal: Proposal 5 — Synthesis intake suppression during INBOX saturation
---

# Synthesis-to-INBOX deposit pause during saturation — CLAUDE.md and supervisor-tick.sh amendment

## Context

INBOX is at 13 items and growing ~4/cycle. The synthesis job (including this one) deposits proposals into INBOX via the tick dispatcher. When INBOX is saturated, these deposits add noise without adding resolution capacity.

## Proposal

### Part A: CLAUDE.md amendment

Add a new entry to `/opt/workspace/CLAUDE.md` under **Automated Self-Reflection Loop**:

```markdown
**Synthesis-to-INBOX deposit pause during saturation.** When INBOX holds >10 items and the consumption rate has been 0 for 3+ consecutive synthesis cycles, the synthesis job should write proposals to `runtime/.meta/cross-cutting-*.md` only (the existing behavior) but the tick dispatcher should NOT create corresponding `supervisor/handoffs/INBOX/` items until the backlog falls below 8. The synthesis file + `LATEST_SYNTHESIS` pointer remain the escalation surface. Rationale: depositing work orders into a queue that is not being processed degrades the queue's signal-to-noise ratio without increasing throughput.
```

### Part B: supervisor-tick.sh enforcement gate

The tick dispatcher (`supervisor-tick.sh`) must check INBOX item count before depositing synthesis proposals. A sketch of the gate:

**Pseudocode location:** Before the section where synthesis-to-INBOX deposits occur (likely near the synthesis translation call).

```bash
# Synthesis-to-INBOX deposit pause during saturation.
# Count current INBOX items.
INBOX_COUNT=$(ls -1 /opt/workspace/supervisor/handoffs/INBOX/*.md 2>/dev/null | wc -l)

# Check if INBOX is saturated (>10 items, 0 consumption recently).
if (( INBOX_COUNT > 10 )); then
  # Count how many recent synthesis cycles had 0 consumption.
  # This is heuristic: if INBOX size hasn't shrunk in 3+ cycles, pause deposits.
  # Implementation detail: may check synthesis file timestamps vs INBOX mtime,
  # or track an explicit counter in a state file.
  pause_deposits=true
else
  pause_deposits=false
fi

# Pass this flag to synthesis-translator or skip deposit entirely if true.
if [[ "$pause_deposits" != "true" ]]; then
  # emit handoffs as normal
else
  # synthesis job ran, but skip INBOX deposits until backlog clears
  echo "supervisor-tick: pausing synthesis-to-INBOX deposits (INBOX saturation)"
fi
```

**Implementation note:** The exact gate logic (how to detect "0 consumption for 3+ cycles") is implementation-detail; the requirement is that when INBOX is visibly saturated and not being consumed, new synthesis proposals should not be deposited into INBOX.

## Verification before action (required)

- Run `grep -n "INBOX.*saturation\|Synthesis.*deposit" /opt/workspace/CLAUDE.md` to confirm the rule is not already present.
- Run `ls -1 /opt/workspace/supervisor/handoffs/INBOX/*.md 2>/dev/null | wc -l` to check current INBOX item count.
- Read `/opt/workspace/supervisor/scripts/lib/supervisor-tick.sh` to identify where synthesis proposals are currently deposited into INBOX and where the gate should be inserted.

## Acceptance criteria

- The CLAUDE.md rule is added to "Automated Self-Reflection Loop" section with the exact text above.
- The supervisor-tick.sh script includes a gate that checks INBOX count before depositing synthesis proposals.
- When INBOX >10 and consumption has stalled, the deposit pause is active (deposits skipped until backlog clears).
- Two commits are created:
  1. "Add synthesis-to-INBOX deposit pause rule to CLAUDE.md"
  2. "Implement INBOX saturation gate in supervisor-tick.sh"
- Both commits use imperative mood and explain why.

## Escalation

URGENT if:
- The CLAUDE.md rule already exists (proposal is already landed; write completion report instead).
- The supervisor-tick.sh deposit logic is unclear or substantially different from expected (may require manual integration).
- The gate introduces syntax errors or breaks the tick dispatcher (test with `bash -n`).
