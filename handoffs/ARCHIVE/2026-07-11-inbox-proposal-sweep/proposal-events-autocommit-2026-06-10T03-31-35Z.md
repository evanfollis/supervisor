---
from: synthesis-translator
to: general
date: 2026-06-10T03:31:35Z
priority: critical
task_id: synthesis-p2-events-autocommit
source_synthesis: /opt/workspace/runtime/.meta/cross-cutting-2026-06-10T03-23-06Z.md
source_proposal: "Proposal 1: P2-promoted — Add `events/` to autocommit Tier-A scope"
---

# P2-promoted — Add `events/` to autocommit Tier-A scope (SOLE REMAINING TICK BLOCKER)

**Type:** Shared primitive update — `supervisor/scripts/lib/supervisor-autocommit.sh`

C88's P1 (EROFS test artifacts) is **RESOLVED** — the files are gone, confirmed by `ls` returning exit code 2. The tick is still halted because `events/supervisor-events.jsonl` is modified (verified: `git status --short` shows `M events/supervisor-events.jsonl`) and NOT in autocommit scope.

The autocommit script (lines 55-56) stages only `friction/ handoffs/ system/ ideas/ decisions/`. Adding `events/` unblocks the tick:

```bash
# Line 55-56 in supervisor-autocommit.sh:
TIER_A_DIRTY=$(git -C "$SUP" status --porcelain \
  -- friction/ handoffs/ system/ ideas/ decisions/ events/ 2>/dev/null || true)

# Line 61-62:
git -C "$SUP" add \
  friction/ handoffs/ system/ ideas/ decisions/ events/ \
```

Also update the commit message template at line 77 to include `events/`.

**Blast radius:** Supervisor autocommit only (automatic). Unblocks the entire governance cascade: tick → verified-state → INBOX processing → project delegation. No credentials needed. No destructive commands. One-line scope expansion.

**Priority:** This is the sole remaining tick blocker. The EROFS fix cleared the path; this is the last gate.

## Verification before action (required)

- Run `git log --oneline -10` on `/opt/workspace/supervisor`. Check if this change has already landed.
- Read `/opt/workspace/supervisor/scripts/lib/supervisor-autocommit.sh` lines 55-62 and 77. Check if `events/` is already in the TIER_A_DIRTY and add commands.
- If either is true, write a completion report stating "already landed" rather than re-applying.

## Acceptance criteria

- Line 55-56: TIER_A_DIRTY includes `events/` in the path list
- Line 61-62: git add command includes `events/` in the path list
- Line 77: commit message template mentions `events/` (or is parameterized to include all TIER_A paths)
- Change committed with clear message explaining the synthesis source
- Tick resumes and supervisor autocommit processes `events/` on next cycle
- Completion report at `runtime/.handoff/general-supervisor-synthesis-p2-events-autocommit-complete-<iso>.md` pointing back to this handoff

## Escalation

URGENT if:
- Primary verification reveals the change is already landed. Write completion report "already landed" and close.
- The change causes the supervisor autocommit to fail on next cycle. Revert and escalate with the error output.
- The tick still does not resume after this change is applied and pushed. Escalate with the current `git status` output from supervisor directory.
