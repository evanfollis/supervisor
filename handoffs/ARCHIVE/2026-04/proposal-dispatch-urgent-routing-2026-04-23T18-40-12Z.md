---
from: synthesis-translator
to: general
date: 2026-04-23T18-40-12Z
priority: critical
task_id: synthesis-dispatch-urgent-routing
source_synthesis: /opt/workspace/runtime/.meta/cross-cutting-2026-04-23T15-24-05Z.md
source_proposal: Proposal 2 — Fix `dispatch-handoffs.sh` URGENT routing (6th cycle, CRITICALLY OVERDUE)
---

# Fix `dispatch-handoffs.sh` URGENT routing (6th cycle, CRITICALLY OVERDUE)

## Problem

`dispatch-handoffs.sh` silently discards URGENT-prefixed handoff files because the `target_session_for()` function matches filenames by checking if the stem starts with a known session name. Files prefixed with `URGENT-` never match because `URGENT` isn't a session name. They hit the empty-target branch and are marked as dispatched without delivery.

**Current behavior:** 6 URGENT files sit in `runtime/.handoff/` where the `general` session never looks. They are silently discarded by `dispatch-handoffs.sh` (lines 52–64, session-prefix matching algorithm doesn't account for priority prefixes).

This bug has been present for at least 6 cycles. Currently 6 URGENT files have been silently discarded by this bug — 2 with expiring deadlines (valuation probes with `stale_close_date: 2026-04-24`, tonight UTC).

## Proposed Fix

**File**: `supervisor/scripts/lib/dispatch-handoffs.sh` lines 52–84

**Change 1:** Update `target_session_for()` to strip known prefixes before matching:

```bash
target_session_for() {
  local filename="$1"
  local stem="${filename%.md}"
  # Strip priority prefix before session-name matching
  stem="${stem#URGENT-}"
  local best=""
  for sess in "${KNOWN_SESSIONS[@]}"; do
    if [[ "$stem" == "${sess}-"* ]]; then
      if (( ${#sess} > ${#best} )); then
        best="$sess"
      fi
    fi
  done
  echo "$best"
}
```

**Change 2:** URGENT-prefixed files that match no session should NOT be silently marked as dispatched. They should be routed to the `general` session's INBOX:

```bash
if [[ -z "$target" ]]; then
  # URGENT files with no session target go to supervisor INBOX
  if [[ "$base" == URGENT-* ]]; then
    cp "$f" "/opt/workspace/supervisor/handoffs/INBOX/$base"
  fi
  mark_dispatched "$f"
  continue
fi
```

**Blast radius:** Handoff dispatcher only. Automatic. All projects benefit. Currently 6 URGENT files have been silently discarded — 2 with expiring deadlines.

## Rationale

The current implementation has two compounding failures:
1. No deduplication for identical root causes
2. Broken URGENT routing that silently discards files whose names start with `URGENT-`

Combined with Pattern #2 ("Escalation surface collapse"), project-level URGENT files are invisible to the `general` session (which checks INBOX, not `runtime/.handoff/`), and the dispatcher throws them away without any signal.

Evidence: The valuation-reflection at 14:20Z states "URGENT handoffs filed at the project level are currently invisible to the principal's primary entry point" and notes deadlines expiring tonight.

## Verification before action (required)

- Run `git log --oneline -20 supervisor/scripts/lib/dispatch-handoffs.sh` in `/opt/workspace/supervisor/`. Check if this exact change has already landed.
- Read the target file. Locate the `target_session_for()` function (around lines 52–84). Verify it does NOT strip the `URGENT-` prefix.
- Check `runtime/.handoff/` for files starting with `URGENT-`. These should exist if the bug is still active.
- If verification shows the fix is already applied, write a completion report stating "already landed" rather than re-applying.

## Acceptance criteria

- The `target_session_for()` function is updated to strip the `URGENT-` prefix before session-name matching.
- The empty-target branch is updated to route `URGENT-*` files to supervisor INBOX instead of silently discarding them.
- Existing URGENT files in `runtime/.handoff/` are manually moved to supervisor INBOX (or processed by the next dispatcher run after the fix is applied).
- Change is committed with a message explaining the fix (e.g., "Fix dispatch-handoffs URGENT routing — previously silently discarded URGENT-prefixed files").
- Completion report confirms fix is applied, lists any URGENT files that were orphaned, and provides the commit SHA.

## Escalation

URGENT if:
- The change is already applied (skip with "already landed" note).
- Verification shows file paths or line numbers have drifted. Escalate with the new locations.
- The fix causes the dispatcher to route files to the wrong session. Escalate with the routing failure named.
