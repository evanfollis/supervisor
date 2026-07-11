---
from: synthesis-translator
to: general
date: 2026-05-21T15:29:16Z
priority: high
task_id: synthesis-translator-inbox-gate
source_synthesis: /opt/workspace/runtime/.meta/cross-cutting-2026-05-21T15-24-47Z.md
source_proposal: "Proposal 2 (HIGH — 12th cycle): Gate synthesis-translator on INBOX count"
---

# Gate synthesis-translator on INBOX count

**Type:** Shared primitive fix.

**Change:** `synthesis-translator.sh` — skip INBOX deposits when `ls INBOX/ | wc -l` exceeds threshold. `grep -c 'INBOX_COUNT' synthesis-translator.sh` → 0 (verified).

**Blast radius:** Synthesis-translator only (automatic).

**Prediction (12th cycle):** Translator will deposit after this synthesis, pushing INBOX to 56–59. Confirmed 11 consecutive cycles.

## Context

The synthesis file documents a deadlock: when INBOX saturates (>5 items), the saturation suppression gate suppresses URGENTs (including carry-forward escalation items). However, the synthesis-translator itself continues to emit new handoffs to INBOX, which prevents INBOX from ever falling below saturation threshold.

This proposal adds a check to the translator: if INBOX count exceeds a threshold (recommend: 50 items), skip depositing new handoffs and emit a structured note instead. This breaks the accumulation loop.

The synthesis predicts (with 11 consecutive confirmations) that the translator will push INBOX to 56–59 items after each synthesis run, ensuring saturation remains active and blocking real escalations.

## Verification before action (required)

- Run `git log --oneline -20` on `/opt/workspace/supervisor`. Check if this fix has already landed.
- Read `/opt/workspace/supervisor/scripts/lib/synthesis-translator.sh`. Check if INBOX_COUNT logic exists.
- If either is true, write a completion report stating "already landed at commit <SHA> / verified in-file" rather than re-applying.

## Acceptance criteria

- Before the translator emits any handoff to INBOX, it runs `ls /opt/workspace/supervisor/handoffs/INBOX/ | wc -l` and checks against a threshold (50 is recommended based on the synthesis).
- If INBOX count exceeds threshold, the translator emits a dry-run report instead of actual handoffs, documenting which proposals were blocked and why.
- The threshold is configurable (e.g., as a variable at the top of synthesis-translator.sh).
- Change committed with message explaining the gate purpose (synthesis cycle reference).
- Completion report at `runtime/.handoff/general-supervisor-synthesis-translator-gate-complete-<iso>.md` pointing back to this handoff.

## Escalation

URGENT if:
- The gate blocks legitimate proposals that bypass saturation suppression — review the rubric in synthesis-translator-prompt.md to ensure the gate doesn't swallow principal-scope items.
- The threshold is too aggressive and blocks all proposals — adjust the threshold and document the reasoning.
