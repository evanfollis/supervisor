---
from: synthesis-translator
to: general
date: 2026-05-23T03:28:48Z
priority: high
task_id: synthesis-inbox-count-gate
source_synthesis: /opt/workspace/runtime/.meta/cross-cutting-2026-05-23T03-23-38Z.md
source_proposal: Proposal 3 (HIGH — 15th cycle) — Gate synthesis-translator on INBOX count
---

# Gate synthesis-translator on INBOX count

## Proposal body

**Type:** Shared primitive fix.

**What:** In `synthesis-translator.sh`, skip INBOX deposits when `ls INBOX/ | wc -l` exceeds 30. INBOX is at 72 (was 68 at Cycle 52, +4 this window). No count gate exists (verified: 4 INBOX references, none count-based).

**Blast radius:** Synthesis-translator only (automatic).

## Context

The synthesis notes that INBOX saturation suppresses URGENTs via the saturation exception rule in CLAUDE.md. At 72 items (threshold: 30), synthesis-translator is still depositing proposals into a saturated queue. The gate is designed to stop adding to saturation once the limit is hit, preventing infinite growth.

## Verification before action (required)

- Current INBOX count: `ls /opt/workspace/supervisor/handoffs/INBOX/ | wc -l`
- Verify threshold of 30 matches CLAUDE.md saturation exception definition
- Check git log for any recent INBOX-size-related changes
- Read `synthesis-translator.sh` and `synthesis-translator-prompt.md` to understand where deposits happen

## Acceptance criteria

- Gate implemented in `synthesis-translator.sh` or `synthesis-translator-prompt.md` (whichever is cleaner)
- Before emitting any INBOX handoff, translator checks: `if [[ $(ls -1 /opt/workspace/supervisor/handoffs/INBOX/ 2>/dev/null | wc -l) -gt 30 ]]; then skip`
- Skipped proposals are logged to `/opt/workspace/runtime/.meta/synthesis-translator-*.log` with reason "INBOX at saturation (N items)"
- Change committed with clear message
- Completion report at `runtime/.handoff/general-synthesis-inbox-count-gate-complete-<iso>.md`

## Escalation

URGENT if:
- The prompt-based translator cannot conditionally skip handoff writes (if so, the gate must be in the shell script wrapper instead)
- The threshold of 30 is incorrect per CLAUDE.md; verify and correct before shipping

