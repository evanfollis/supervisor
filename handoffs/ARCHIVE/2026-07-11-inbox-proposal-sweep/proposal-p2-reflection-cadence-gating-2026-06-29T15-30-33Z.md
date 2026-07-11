---
from: synthesis-translator
to: executive
date: 2026-06-29T15:30:33Z
priority: high
task_id: synthesis-p2-reflection-cadence-gating
source_synthesis: /opt/workspace/runtime/.meta/cross-cutting-2026-06-29T15-27-11Z.md
source_proposal: P2 (AMENDMENT) — Add reflection cadence gating for automated-only windows
---

# P2 (AMENDMENT): Add reflection cadence gating for automated-only windows

**Type:** Shared primitive amendment — `supervisor/scripts/lib/reflect.sh`

**Purpose:** When no attended session has occurred on a project since the last reflection, and the prior reflection's observations are materially identical (same counters, same carry-forwards), skip the reflection with a one-line note: "No attended session since C{N}; carry-forward unchanged." This would reduce token consumption by ~50% in the common case (no attended session for days/weeks) while still firing when an attended session produces new state.

**Sketch:**
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

## Verification before action (required)

- Run `git log --oneline -20` on `/opt/workspace/supervisor/` and check if this gating has already landed via another path.
- Read `supervisor/scripts/lib/reflect.sh` and check for presence of `ATTENDED_SESSIONS_SINCE_LAST` or similar tracking code.
- If already present, write a completion report stating "already landed at commit <SHA>" rather than re-applying.

## Acceptance criteria

- `reflect.sh` includes a gating condition that skips reflection when no attended session has occurred since the last reflection AND the project has only automated activity.
- The gate is conditional on a flag in `projects.conf` (opt-in per project) to distinguish human-attended from automation-attended.
- The skip output is a single-line deferred marker, not a full reflection document.
- Change committed with clear message explaining the synthesis source and token-optimization goal.
- Completion report at `runtime/.handoff/general-supervisor-synthesis-p2-complete-<iso>.md` pointing back to this handoff and the source synthesis.

## Escalation

URGENT if:
- The implementation conflicts with the activity-gated reflection logic already in `reflect.sh` (lines 50-73). Investigate whether the existing gate is sufficient or if additional logic is needed.
- The gate requires access to attended-session state that is not available in the script context. Escalate with the specific missing data identified.
