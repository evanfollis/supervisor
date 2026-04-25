---
from: synthesis-translator
to: general
date: 2026-04-24T15-33-47Z
priority: high
task_id: synthesis-supervisor-autocommit-oscillation
source_synthesis: /opt/workspace/runtime/.meta/cross-cutting-2026-04-24T15-23-45Z.md
source_proposal: Proposal 2 — Fix supervisor autocommit oscillation
---

# Fix supervisor autocommit oscillation

## Context
Pattern 3 in the synthesis: Supervisor tick blocked 16h+ by autocommit/archive oscillation. A file (ADR-0031) oscillates between tracked and untracked state between autocommit cycles, producing a perpetually dirty tree that triggers the safety guard in `supervisor-tick.sh`. Combined with the prior window, this is 16h+ of tick blockage.

The synthesis notes: "The supervisor's own governance tick has been blocked for the entire 12h window — 7 consecutive dirty-tree skips, escalated via URGENT."

## Proposed Change

Modify `supervisor-autocommit.sh` Tier-A tracking to either:

**Option A (safer, surgical)**: Exclude `decisions/0031-*` or the specific oscillating path from the Tier-A autocommit scope.

**Option B (more robust)**: Restructure so that the archive-deletion and commit happen as one atomic operation, eliminating the window where the file toggles state.

The synthesis strongly recommends Option A as the immediate fix, pending investigation of why ADR-0031 oscillates.

## Implementation Details

**Where**: `supervisor/scripts/lib/supervisor-autocommit.sh` — line 55 and the matching git add on line 62–63.

**Option A**: Add a filter to exclude ADR-0031 from Tier-A tracking:
```bash
# Line 54–55: modify the TIER_A_DIRTY check
TIER_A_DIRTY=$(git -C "$SUP" status --porcelain \
  -- friction/ handoffs/ system/ ideas/ 'decisions/*' ':!decisions/0031-*' 2>/dev/null || true)

# Line 62–63: also exclude from the add
git -C "$SUP" add \
  friction/ handoffs/ system/ ideas/ 'decisions/*' ':!decisions/0031-*' \
  2>/dev/null || true
```

**Option B**: Requires deeper restructuring of the autocommit flow — defer pending investigation.

## Verification before action (required)

- Run `git log --oneline -20 supervisor/scripts/lib/supervisor-autocommit.sh` to check if this is already fixed.
- Run `git diff HEAD -- decisions/0031-* 2>/dev/null | wc -l` to confirm ADR-0031 has recent changes.
- Check the most recent supervisor tick output to understand the oscillation pattern: `tail -100 /opt/workspace/runtime/.supervisor-tick.log 2>/dev/null` or check systemd journal for `workspace-session@general.service`.

## Critical prerequisite investigation

**BLOCKING**: The synthesis asks as a question for the human: "What creates and deletes ADR-0031 between cycles?"

Before implementing Option A, investigate:
1. Does ADR-0031 get created/deleted by the synthesis job?
2. Does it get created/deleted by the archive script mentioned in the synthesis?
3. Is it ephemeral working output that should move out of `decisions/`?
4. Is there a periodic autogeneration loop creating it?

If ADR-0031 should be tracked but is being created/deleted as an artifact of another process, the real fix is to stabilize that process, not to surgically exclude the file. Run `grep -r "0031" /opt/workspace/supervisor/scripts/lib/ /opt/workspace/supervisor/supervisor-*.sh 2>/dev/null` to find what touches it.

## Blast radius

**Medium.** Supervisor-autocommit.sh is shared infrastructure. The fix must not accidentally exclude legitimate governance artifacts from tracking. Option A is surgical (one file exclusion) but requires understanding why ADR-0031 oscillates. If the oscillation is actually a bug in another process (file being created/deleted when it shouldn't be), the fix is to stabilize that process, not to exclude the symptom.

## Acceptance criteria

- Supervisor tick runs without dirty-tree blockage for ≥3 consecutive cycles (6h)
- Option A applied with justification explaining why ADR-0031 oscillation is expected / documented in code
- OR Option B implemented with atomic archive/commit flow documented
- No other governance artifacts are accidentally dropped from autocommit tracking
- Completion report includes the root-cause investigation of what was creating/deleting ADR-0031

## Escalation

URGENT if:
- Investigation reveals ADR-0031 is being created/deleted by a process that should not be doing so (e.g. the archive script is buggy) — escalate to fix the root cause, not suppress the symptom
- The oscillation is tied to a recent change in another script — coordinate with that change before applying this fix
- ADR-0031 is legitimate governance output that should be tracked — don't exclude it; fix the upstream process creating/deleting it

## Standing note

The supervisor reflection suspects the `archive-inbox-session-summaries.sh` script is eating non-session-summary INBOX items, but the script's glob on line 16 is `session-summary-*.md` only — it cannot match URGENT-prefixed files. That diagnosis appears incorrect. The real ADR-0031 oscillation has an unknown root cause that this investigation must surface.
