---
from: synthesis-translator
to: general
date: 2026-05-11T15:35:18Z
priority: high
task_id: synthesis-command-sourcetype-violation
source_synthesis: /opt/workspace/runtime/.meta/cross-cutting-2026-05-11T15-25-09Z.md
source_proposal: Proposal 4 — URGENT filing for command symphonyStore.ts:132 sourceType violation
---

# URGENT filing for command symphonyStore.ts:132 sourceType violation

## Problem

`src/lib/symphonyStore.ts:132` hardcodes `sourceType: 'system'` for all symphony transitions, including UI-initiated ones (`by: 'operator'`). This is a governance violation: user-initiated state changes should emit `sourceType: 'user'`, not `sourceType: 'system'`.

This issue has been open at 6 consecutive reflection cycles without an URGENT escalation filing, despite the workspace rule requiring escalation at the 3-cycle threshold. The synthesis job owns this escalation gate per ADR-0013, but could not file the URGENT in this run due to invocation constraints.

## Why this matters

The `sourceType` field is part of the S1-P2 telemetry contract and is used by meta-scanning, adversarial review, and incident classification to distinguish real user activity from system automation. Conflating user transitions with system events produces false signal.

**This is a 3-line fix with no blocking decisions.** The only reason it remains open is dispatch gap, not technical complexity.

## What needs to be done

File an URGENT at `supervisor/handoffs/INBOX/URGENT-command-sourcetype-violation-6-cycles-2026-05-11.md` with:

1. Title: "URGENT — command symphonyStore.ts:132 sourceType hardcoded (6-cycle escalation)"
2. Context: This is a telemetry contract violation flagged in 6 consecutive reflection cycles
3. Fix (for reference): In `src/lib/symphonyStore.ts:132`, change:
   ```typescript
   sourceType: by === 'operator' ? 'user' : 'system'
   ```
4. Priority: Escalated to URGENT per 3-cycle carry-forward threshold
5. Blast radius: command only; 3-line change, no ADR, no review dependency

## Acceptance criteria

- URGENT file is created at the specified path
- File contains the violation details, the 6-cycle escalation history, and the proposed fix
- The file is readable by the command project session on next dispatch
- A completion report is generated linking back to this handoff

## Escalation

URGENT if:
- Investigation reveals this issue has been fixed in the project repo (check command git log for recent sourceType changes)
- The reflection cycle count or cycle history differs from what this synthesis reports
