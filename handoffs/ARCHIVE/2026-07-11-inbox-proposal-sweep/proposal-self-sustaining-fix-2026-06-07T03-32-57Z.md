---
from: synthesis-translator
to: general
date: 2026-06-07T03:32:57Z
priority: high
task_id: synthesis-self-sustaining-fix
source_synthesis: /opt/workspace/runtime/.meta/cross-cutting-2026-06-07T03-27-00Z.md
source_proposal: 1. P-self-sustaining-fix — Exclude automation-generated activity from reflect.sh inactivity check
---

# P-self-sustaining-fix — Exclude automation-generated activity from reflect.sh inactivity check

**Type:** Shared primitive update — `supervisor/scripts/lib/reflect.sh`

**Context:** The reflection → synthesis → INBOX pipeline is functional but lacks a convergence-aware cadence reduction. It runs at full throughput (36 Claude Sonnet sessions/day) regardless of whether output channels are being consumed. Self-generated telemetry and reflect-session JSONL are counted as activity, preventing the inactivity check from short-circuiting and reducing wasted sessions during dormancy.

**Proposed change (2 locations):**

**Line 60:** Filter out self-generated telemetry:
```bash
# Line 60: exclude self-generated telemetry
TELEMETRY_COUNT=$(tail -n 5000 "$WORKSPACE_TELEMETRY_DIR/events.jsonl" 2>/dev/null \
  | grep -F "\"$PROJECT\"" \
  | grep -v '"source":"session-end-auto-summary"' \
  | grep -v '"source":"reflect"' \
  | wc -l || true)
```

**Lines 64–67:** Exclude reflect-session JSONL from activity check:
```bash
# Lines 64-67: exclude reflect-session JSONL
JSONL_RECENT=$(find "$SESSION_DIR" -maxdepth 1 -name '*.jsonl' \
  -not -name '*reflect*' -newermt "12 hours ago" 2>/dev/null | wc -l)
```

**Blast radius:** All 8 projects (automatic). Reduces wasted sessions from ~36/day to ~4/day during dormancy. Independent of P1 (destructive git clean).

**Rationale:** The observation system generates its own artifacts, which are counted as activity, which prevents the inactivity gate from working. Breaking this cycle eliminates ~32 wasted sessions/day.

## Verification before action (required)

- Run `git log --oneline -20 supervisor/scripts/lib/reflect.sh` to check if this has landed via another path.
- Read `supervisor/scripts/lib/reflect.sh` lines 56–67. Verify they do NOT contain `grep -v '"source"` filters or `find ... -not -name '*reflect*'`.
- If either verification fails, write a completion report stating which commit this was already landed in.

## Acceptance criteria

- Line 60 is updated to filter `'"source":"session-end-auto-summary"'` and `'"source":"reflect"'` from telemetry count.
- Lines 64–67 are updated to exclude files matching `*reflect*.jsonl` from the activity check.
- Change committed with a message explaining the synthesis source (e.g., "Reduce self-sustaining observation loop — exclude automation-generated activity from reflect.sh inactivity check (synthesis C83)").
- No adversarial review required (straightforward logic fix with narrow blast radius).
- Completion report written to `/opt/workspace/supervisor/handoffs/INBOX/completion-self-sustaining-fix-<iso>.md` with a brief summary of the change and expected impact.

## Escalation

URGENT if:
- Primary verification reveals this has already landed. Record the commit hash and close.
- The proposed change conflicts with a more recent modification to the same lines. Surface the conflict with both versions.
