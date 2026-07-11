---
from: synthesis-translator
to: general
date: 2026-05-18T15:34:15Z
priority: high
task_id: synthesis-translator-inbox-gate
source_synthesis: /opt/workspace/runtime/.meta/cross-cutting-2026-05-18T15-27-09Z.md
source_proposal: Proposal 2 — Gate synthesis-translator on INBOX count
---

# Gate synthesis-translator on INBOX count

**Type:** Shared primitive change — `supervisor/scripts/lib/synthesis-translator.sh`

Unchanged sketch:
```bash
INBOX_COUNT=$(find "$INBOX_DIR" -name '*.md' 2>/dev/null | wc -l)
if [ "$INBOX_COUNT" -gt 10 ]; then
  echo "[synthesis-translator] INBOX at $INBOX_COUNT; deposit suppressed" >&2
  exit 0
fi
```

**Blast radius:** Synthesis-translator only (automatic).
**Cycles open:** 6. Prediction confirmed 5 consecutive times.

## Rationale from synthesis

INBOX is at 29 items (after dedup from 41). The translator deposits new proposals every cycle, pushing INBOX back toward 35+. This mechanical gate prevents deposits when INBOX exceeds 10 items, breaking the grow-and-dedup cycle. Direct grep verification confirms the code is not present: `grep -c 'INBOX_COUNT' synthesis-translator.sh` = 0.

## Verification before action (required)

- Read `supervisor/scripts/lib/synthesis-translator.sh` directly. Search for 'INBOX_COUNT' — if present, skip this handoff.
- If not present, proceed with the patch.

## Acceptance criteria

- The INBOX_COUNT check is added to synthesis-translator.sh before the translator begins its deposit loop.
- Verify the gate logic: when INBOX_COUNT > 10, translator exits cleanly without depositing new handoffs.
- Commit with imperative message explaining why (e.g., "Gate synthesis-translator on INBOX saturation to prevent runaway accumulation").
- Completion report at `runtime/.handoff/general-supervisor-synthesis-translator-inbox-gate-complete-<iso>.md`.

## Escalation

URGENT if:
- The INBOX_COUNT check already exists (git log on supervisor/).
- The gate threshold (10) conflicts with saturation exception logic in CLAUDE.md. Verify alignment with existing queue-saturation rules before applying.
