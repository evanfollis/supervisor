---
from: synthesis-translator
to: general
date: 2026-04-23T18-40-12Z
priority: high
task_id: synthesis-urgent-handoff-startup-scan
source_synthesis: /opt/workspace/runtime/.meta/cross-cutting-2026-04-23T15-24-05Z.md
source_proposal: Proposal 5 — `general` session startup scans `runtime/.handoff/URGENT-*` (2nd cycle)
---

# `general` session startup scans `runtime/.handoff/URGENT-*` (2nd cycle)

## Problem

The `general` session reads `supervisor/handoffs/INBOX/` during startup (via `session-start-context-load.sh` hook) but does not scan `runtime/.handoff/`. Project-level URGENT files are completely invisible at the executive level.

**Evidence:** The valuation URGENT with tonight's deadline (Apr 24 `stale_close_date`) has been at `runtime/.handoff/URGENT-skillfoundry-valuation-...` for 84h+ without reaching the principal or any attended session. It only surfaced through reflection cycles (which are read-only, unattended).

## Proposed Fix

**Option A (preferred):** Add to the `session-start-context-load.sh` hook

Append to the end of `/root/.claude/hooks/session-start-context-load.sh`:

```bash
urgent_handoffs=$(ls /opt/workspace/runtime/.handoff/URGENT-* 2>/dev/null)
if [[ -n "$urgent_handoffs" ]]; then
  echo "=== URGENT project handoffs awaiting triage ==="
  echo "$urgent_handoffs"
fi
```

This makes project-level URGENTs visible every time the `general` session starts.

**Option B (alternative):** Add to the executive reentry checklist in `supervisor/CLAUDE.md`

If the hook approach is not preferred, add a line to the "When the `general` session" section of `/opt/workspace/CLAUDE.md` to explicitly document that the executive should check `runtime/.handoff/URGENT-*` on each session start.

**Blast radius:** `general` session startup only. Low risk. Makes project-level urgencies visible at the executive level. Complementary to Proposal 2 (which fixes the routing; this fixes the visibility).

## Rationale

This is the 2nd cycle recommending visibility of project-level URGENTs at the executive level. Combined with Proposal 2 (fixing `dispatch-handoffs.sh` routing), project-level URGENT files will:
1. Be routed correctly (not discarded)
2. Be visible to the `general` session at startup (not hidden in `runtime/.handoff/`)

Together, these two proposals close the escalation channel from projects to executive.

## Verification before action (required)

- Read `/root/.claude/hooks/session-start-context-load.sh`. Check if it already has code to scan `runtime/.handoff/URGENT-*`.
- Check `/opt/workspace/runtime/.handoff/` for files starting with `URGENT-`. Count them. These are the files that should be visible to the executive.
- If the hook already scans for URGENT files, write a completion report stating "already implemented" rather than re-applying.
- If the hook does not scan, verify this is the correct place to add the change (it should fire at every session start for the `general` session).

## Acceptance criteria

**If Option A (hook):**
- The scan code is appended to `/root/.claude/hooks/session-start-context-load.sh`.
- On the next `general` session start, the hook outputs "=== URGENT project handoffs awaiting triage ===" followed by a list of any `URGENT-*` files in `runtime/.handoff/`.
- No changes to project files are needed (hook is shared across all sessions).
- Change is committed with a message explaining the addition (e.g., "Add URGENT handoff scan to session-start hook").
- Completion report confirms the hook is updated, provides a sample of the output, and gives the commit SHA.

**If Option B (charter):**
- A line is added to the `supervisor/CLAUDE.md` "When the `general` session" section documenting the check.
- The text explains that the executive should scan `runtime/.handoff/URGENT-*` on each session start.
- Change is committed with a message explaining the documentation.
- Completion report confirms the rule is documented and provides the commit SHA.

## Escalation

URGENT if:
- Verification shows the hook already performs this scan. Skip with "already implemented" note.
- The hook approach is rejected in favor of charter documentation. Implement Option B instead and note the rationale in the completion report.
- The scan logic discovers that `runtime/.handoff/URGENT-*` files are being created by a different source than expected (not just projects). Escalate to clarify which files should be visible to the executive.
