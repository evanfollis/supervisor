---
from: synthesis-translator
to: general
date: 2026-06-15T15:34:28Z
priority: high
task_id: synthesis-p-autocommit-archive-target
source_synthesis: /opt/workspace/runtime/.meta/cross-cutting-2026-06-15T15-26-25Z.md
source_proposal: "Proposal 2 — P-autocommit-archive-target (NEW — from supervisor C40 OBS-2)"
---

# P-autocommit-archive-target

**Type:** Shared primitive fix.
**File:** `supervisor/scripts/lib/supervisor-autocommit.sh`

## Problem

Session-summary archives are being deposited into `handoffs/INBOX/` rather than `handoffs/ARCHIVE/`. This mechanically inflates the INBOX by ~4 items per autocommit cycle, contaminating the proposal queue signal even when no proposals exist.

## Solution

Change the deposit path for session-summary archives from `handoffs/INBOX/` to `handoffs/ARCHIVE/$(date +%Y-%m)/`.

Sketch:
```bash
# Current (deposits to INBOX):
# cp "$summary" "$SUP/handoffs/INBOX/session-summary-${project}-${ts}.md"

# Fixed (deposit to ARCHIVE):
ARCHIVE_DIR="$SUP/handoffs/ARCHIVE/$(date +%Y-%m)"
mkdir -p "$ARCHIVE_DIR"
cp "$summary" "$ARCHIVE_DIR/session-summary-${project}-${ts}.md"
```

## Verification before action (required)

- Run `git log --oneline -20` on supervisor repo. Check if this fix has already landed.
- Read `supervisor/scripts/lib/supervisor-autocommit.sh` and search for any session-summary archive deposit logic.
- If the logic already deposits to `ARCHIVE/`, write a completion report stating "already landed" rather than re-applying.

## Acceptance criteria

- Session-summary archives are deposited to `handoffs/ARCHIVE/<year>-<month>/` instead of `handoffs/INBOX/`.
- The `ARCHIVE_DIR` is created if it doesn't exist (mkdir -p).
- Change committed with clear message: "Route session-summary archives to ARCHIVE, not INBOX (synthesis C100, Pattern 2)".
- INBOX count stabilizes (mechanical inflation ~8 items/day stops).

## Note

This does not affect the existing 185 items already in INBOX — those will need a separate triage pass. This fix stops new inflation.

## Escalation

URGENT if:
- The session-summary logic is not found in the file. The deposit target may have been moved elsewhere (e.g. a different script). Escalate with the actual current location.
- Primary verification reveals the fix is already landed. Write completion report stating "already landed" and close.
