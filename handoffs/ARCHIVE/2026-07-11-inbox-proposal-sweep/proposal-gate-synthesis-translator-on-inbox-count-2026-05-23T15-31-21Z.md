---
from: synthesis-translator
to: general
date: 2026-05-23T15:31:21Z
priority: medium
task_id: synthesis-translator-inbox-gate
source_synthesis: /opt/workspace/runtime/.meta/cross-cutting-2026-05-23T15-25-20Z.md
source_proposal: "Proposal 4 (CARRY-FORWARD — 16th cycle): Gate synthesis-translator on INBOX count"
---

# Gate synthesis-translator on INBOX count

## Proposal Summary

Implement a count-based gate that prevents the synthesis-translator from emitting new handoffs when INBOX saturation has been reached, reducing noise in the queue.

**What:** Add a check in `supervisor/scripts/lib/synthesis-translator.sh` that aborts handoff generation if `/opt/workspace/supervisor/handoffs/INBOX/` exceeds a threshold count (propose: 50 items) and records the suppression in the synthesis output.

**Status:** Carry-forward from Cycle 53 P3 (unchanged). INBOX at **76** (was 72 at Cycle 53, 68 at Cycle 52). Growth rate ~4/window. No count gate exists. Suppression active.

## Context (from synthesis)

The INBOX queue has grown from 68 items (Cycle 52) → 72 items (Cycle 53) → 76 items (current). At this growth rate, the queue will reach 100+ items within a few cycles without intervention. The synthesis loop continues to emit handoffs even when the queue is saturated, creating noise that obscures truly urgent escalations.

A count gate would:
1. Check INBOX count before the translation loop
2. If over threshold, skip handoff generation for carry-forward proposals (leaving immediate/new proposals intact)
3. Record the decision in the synthesis output so it's visible in the report
4. Allow the executive to track queue saturation without flooding INBOX with meta-proposals

This is a structural fix to prevent the escalation surface from being overwhelmed by its own output.

## Verification before action (required)

- Check if a gate already exists: `grep -r "INBOX.*count" /opt/workspace/supervisor/scripts/lib/`
- Count current INBOX items: `ls /opt/workspace/supervisor/handoffs/INBOX/ | wc -l`
- If gate exists and count is below threshold, write completion report saying "gate already implemented, INBOX count: N"
- If gate exists and is active/suppressing, note the current suppression status in completion report.

## Acceptance criteria

- Modify `supervisor/scripts/lib/synthesis-translator.sh` to:
  - Count items in `/opt/workspace/supervisor/handoffs/INBOX/` at the start of handoff generation
  - If count >= 50 (or agreed threshold), skip translation of carry-forward proposals only; still emit immediate/new proposals
  - Emit a section in the output report noting the suppression: "Synthesis-translator gated: INBOX count N >= threshold 50; carry-forward proposals suppressed"
- Change is committed with message: "Implement INBOX count gate in synthesis-translator (synthesis Cycle 54 P4)"
- Adversarial review not needed (operational gate, policy-level change).
- Completion report at `runtime/.handoff/general-supervisor-synthesis-gate-complete-<iso>.md` pointing back to this handoff.

## Escalation

URGENT if:
- The synthesis-translator script cannot be located or has a different structure than expected.
- The gate implementation requires coordination with the synthesis writer (synthesize.sh) to prevent double-work.
- After gate is in place, INBOX continues to grow above threshold without new executive action — this indicates the gate alone is insufficient and the executive must also increase consumption rate.
