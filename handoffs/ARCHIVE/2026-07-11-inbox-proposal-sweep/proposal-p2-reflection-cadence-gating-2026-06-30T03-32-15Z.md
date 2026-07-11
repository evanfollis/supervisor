---
from: synthesis-translator
to: general
date: 2026-06-30T03:32:15Z
priority: high
task_id: synthesis-p2-reflection-gating
source_synthesis: /opt/workspace/runtime/.meta/cross-cutting-2026-06-29T15-27-11Z.md
source_proposal: P2 - Add reflection cadence gating for automated-only windows
---

# P2: Add reflection cadence gating in reflect.sh

## Full Proposal (from C114)

**Type:** Shared primitive amendment — `supervisor/scripts/lib/reflect.sh`

**Purpose:** When no attended session has occurred on a project since the last reflection, and the prior reflection's observations are materially identical (same counters, same carry-forwards), skip the reflection with a one-line note: "No attended session since C{N}; carry-forward unchanged." This would reduce token consumption by ~50% in the common case (no attended session for days/weeks) while still firing when an attended session produces new state.

**Sketch (from the proposal):**
```bash
# In reflect.sh, after loading prior reflection:
if [ "$ATTENDED_SESSIONS_SINCE_LAST" -eq 0 ] && \
   [ "$AUTOCOMMIT_ONLY" = "true" ]; then
  echo "# Reflection deferred — no attended session since C${PRIOR_CYCLE}" \
    > "$OUTPUT"
  exit 0
fi
```

**Blast radius:** All reflected projects (opt-in via flag in `projects.conf`). The atlas runner is "attended" by the autonomous loop but not by a human; the gating should distinguish human-attended from automation-attended. The supervisor autocommit-only case is the clearest candidate.

**Rationale (from C114):** The reflection and synthesis loops are consuming Opus/Sonnet-tier resources (8 Claude sessions every 12h across 8 projects) to produce materially identical reports. Each cycle faithfully increments counters and carry-forwards, but generates zero new information when no attended session has occurred. This is not a failure of the loop design — the loop correctly identified that it has reached its own ceiling. The observation is that continuing to run at the same cadence when no attended session occurs is spending resources to confirm a known state.

## Verification before action (required)

- Run `git log --oneline -20` on `/opt/workspace`. Check if this gating logic has already landed via another path (commit message would reference P2, reflection cadence, or automated-only).
- Read `/opt/workspace/supervisor/scripts/lib/reflect.sh` lines 50-73 (activity checking section). Verify that it does NOT yet contain the `ATTENDED_SESSIONS_SINCE_LAST` and `AUTOCOMMIT_ONLY` gating logic sketched above.
- If the gating is already present, write a completion report stating "already landed" and close.

## Acceptance criteria

- The gating logic is added to `reflect.sh` after the activity-check block (around line 73, before the reflection prompt rendering)
- The logic correctly:
  - Detects when no attended session has occurred since the last reflection
  - Detects when only automation (autocommit, runner cycles) has occurred
  - Writes a one-line skip message: "# Reflection deferred — no attended session since C{N}; carry-forward unchanged"
  - Exits cleanly without spawning Claude
- Change committed with message: "Add reflection cadence gating for automated-only windows — skip reflections when no attended session and prior observations unchanged" (or similar — explain the why)
- Completion report at `/opt/workspace/supervisor/handoffs/INBOX/general-p2-reflection-gating-complete-<iso>.md` pointing back to this handoff and the source synthesis

## Escalation

URGENT if:
- Primary verification reveals the gating is already landed. Write "obsolete — already landed" and close.
- The implementation conflicts with how `projects.conf` flags are structured. Escalate with the structural conflict named.
- The gating relies on data (e.g., prior cycle number) that is not reliably available. Escalate with the missing data source named.
