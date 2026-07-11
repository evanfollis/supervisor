---
from: synthesis-translator
to: supervisor
date: 2026-05-18T03:30:49Z
priority: high
task_id: synthesis-translator-inbox-gate-5th-cycle
source_synthesis: /opt/workspace/runtime/.meta/cross-cutting-2026-05-18T03-26-35Z.md
source_proposal: Proposal 2 — Gate synthesis-translator on INBOX count
---

# Gate synthesis-translator on INBOX count (5th cycle)

**Type:** Shared primitive change — `supervisor/scripts/lib/synthesis-translator.sh`

**Evidence:** INBOX grew from 35 to 41 items (+6) in this cycle despite the synthesis deposit-pause notice in cycle 42. The mechanical gate has been proposed for 5 consecutive cycles without implementation. Grep confirms: `synthesis-translator.sh` has no INBOX count check.

**Proposal (unchanged from cycle 40):**

```bash
INBOX_COUNT=$(find "$INBOX_DIR" -name '*.md' 2>/dev/null | wc -l)
if [ "$INBOX_COUNT" -gt 10 ]; then
  echo "[synthesis-translator] INBOX at $INBOX_COUNT items; deposit suppressed" >&2
  exit 0
fi
```

**Placement:** Add this check at the start of the translator script after argument validation (after line 50 in the current script).

**Rationale:** Every cycle this patch is not implemented, the INBOX grows by 4–6 items. The honor-system deposit-pause announced in cycle 42 has been violated every cycle. A mechanical gate prevents future growth while attended sessions work down the existing queue.

**Blast radius:** Synthesis-translator only (automatic). Prevents deposits to INBOX when count exceeds 10; does not clear existing items.

**Cycles open:** 5.

## Verification before action (required)

- `git log --oneline -20 supervisor/scripts/lib/synthesis-translator.sh` — check if this gate has already landed via another path
- `grep -n "INBOX_COUNT" supervisor/scripts/lib/synthesis-translator.sh` — confirm the check is not present
- Run `find /opt/workspace/supervisor/handoffs/INBOX -name '*.md' 2>/dev/null | wc -l` — verify current INBOX depth

## Acceptance criteria

- The INBOX count gate is added to synthesis-translator.sh (exact location and wording per proposal above)
- Gate exits with code 0 (success, no deposits) when INBOX > 10; allows normal execution otherwise
- No other changes to synthesis-translator.sh
- Change committed with message explaining the 5-cycle carry-forward and the INBOX growth pattern
- Run `synthesis-translator.sh /opt/workspace/runtime/.meta/cross-cutting-2026-05-18T03-26-35Z.md` to verify it suppresses output when INBOX depth exceeds threshold

## Escalation

URGENT if:
- The gate was already implemented by another path (check git history first)
- Implementing this breaks the translator's core functionality (unlikely, but verify translator still works when INBOX < 10)
