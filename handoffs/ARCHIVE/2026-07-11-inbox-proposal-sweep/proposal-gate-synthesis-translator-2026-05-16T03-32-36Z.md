---
from: synthesis-translator
to: general
date: 2026-05-16T03:32:36Z
priority: high
task_id: synthesis-gate-translator
source_synthesis: /opt/workspace/runtime/.meta/cross-cutting-2026-05-16T03-27-07Z.md
source_proposal: "Proposal 2 — Gate synthesis-translator on INBOX count"
---

# Gate synthesis-translator on INBOX count

The synthesis-translator is the mechanical actor violating the deposit-pause rule for 3 consecutive cycles (cycles 37, 38, 39). The fix is in the translator script itself, not in the synthesis prompt.

## Background

Cycle 37 adopted a deposit-pause rule: no new INBOX items when count >10 and consumption is zero for 3+ cycles. The rule has been violated every cycle since adoption:

- **Cycle 37**: Tick dispatcher deposited 5 items (INBOX 13 → 18).
- **Cycle 38**: Synthesis-translator deposited 3 items (INBOX 18 → 21).
- **Cycle 39**: INBOX now at 24 items.

The underlying failure class: the deposit-pause is a prose rule. The synthesis-translator (`supervisor/scripts/lib/synthesis-translator.sh`) does not check INBOX count before writing. The rule is structurally unenforceable at the current layer until the translator itself is gated.

## Change required

File: `supervisor/scripts/lib/synthesis-translator.sh`

Add the following check early in the script, before writing any handoff files:

```bash
INBOX_COUNT=$(find "$SUP/handoffs/INBOX" -name '*.md' 2>/dev/null | wc -l)
if [ "$INBOX_COUNT" -gt 10 ]; then
  echo "[synthesis-translator] INBOX at $INBOX_COUNT; deposit suppressed" >&2
  exit 0
fi
```

**Placement:** Add this check immediately after the script validates its inputs and before the loop that processes proposals.

## Verification before action (required)

- Read `supervisor/scripts/lib/synthesis-translator.sh` in the current repo.
- Check `git log --oneline -10 supervisor/scripts/lib/synthesis-translator.sh` to see if this gate has already been added.
- If the patch is already in the file, write a completion report stating "already landed at commit <SHA>" rather than re-applying.
- If the file does not exist or cannot be read, escalate with details.

## Blast radius

Synthesis-translator only. Automatic enforcement of the deposit-pause rule. Prevents INBOX growth past 10 from the translator path. Ticks already partially comply via prose; this closes the remaining mechanical gap. No downstream impact on other scripts or projects.

## Acceptance criteria

- The gate check is added to `supervisor/scripts/lib/synthesis-translator.sh`.
- The script is committed with a message explaining the source (synthesis-translator gating, cycle 39 proposal).
- Verification: next synthesis run (at ~03:27Z UTC) either emits a "deposit suppressed" message to stderr (if INBOX >10) or proceeds normally (if INBOX ≤10).
- Adversarial review is not required for this change (trivial, mechanical gate).
- Completion report filed at `runtime/.handoff/general-supervisor-synthesis-gate-translator-complete-<iso>.md`.

## Escalation

URGENT if:
- The script cannot be edited (permission denied, file locked).
- Adding the gate breaks script syntax or execution (test the change locally before committing).
- The gate logic conflicts with other recent changes to the translator (check git log).
