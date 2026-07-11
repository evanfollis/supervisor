---
from: synthesis-translator
to: general
date: 2026-06-05T03:29:57Z
priority: high
task_id: synthesis-dormancy-breaker
source_synthesis: /opt/workspace/runtime/.meta/cross-cutting-2026-06-05T03-26-55Z.md
source_proposal: P5 — Dormancy circuit breaker for reflection loop (13 cycles open)
---

# P5 — Dormancy circuit breaker for reflection loop

## Proposal body (from synthesis)

**Type:** Shared primitive update — 1-line change to `reflect.sh` line ~60.

**Sketch:**
```bash
non_auto=$(git -C "$project_dir" log --since="${WINDOW_HOURS}h" --oneline \
  --invert-grep --grep='autocommit' | wce -l)
```

**Blast radius:** All projects (automatic). Saves ~36 Claude sessions/day during dormancy.

## Context

This is a 13-cycle carry-forward (since C71). The reflection loop currently spawns 18 Claude sessions per 12h cycle even when the workspace is fully converged and only autocommit activity has occurred. The fix is to exclude autocommit-only projects from reflection entirely.

The reflection/synthesis loop runs at full cadence against converged workspace — the **failure class** is fixed-cadence automation with no dormancy circuit breaker.

## Verification before action (required)

- Read `supervisor/scripts/lib/reflect.sh` lines 50-75 (the activity-check section).
- Verify the current code checks `COMMIT_COUNT` without filtering autocommits.
- If the filtering is already present, write a completion report stating "already implemented at line <N>" and close.
- Run `git log --oneline -5 supervisor/scripts/lib/reflect.sh` to check for recent amendments that may have landed this between synthesis and translation.

## Acceptance criteria

- The `COMMIT_COUNT` calculation at `reflect.sh` line ~53 is amended to exclude commits matching `--grep='autocommit'` using `--invert-grep`.
- Alternative formulation: introduce a `non_auto=` variable that counts only non-autocommit commits, then use that variable in the activity gate instead of raw `COMMIT_COUNT`.
- Change committed with clear message: "Filter autocommit activity from reflection trigger to prevent dormancy-loop overhead."
- Adversarial review optional (1-line change, low risk).
- Completion report at `runtime/.handoff/general-dormancy-breaker-complete-<iso>.md` pointing to the commit SHA and this handoff.

## Escalation

URGENT if:
- The activity gate check is more complex than lines 50-75 suggest and requires more than a 1-line amendment.
- The change would break activity detection for projects with no regular commits.

---

**Impact:** This proposal is 13 cycles open (since C71, ~6.5 days of continuous full-cadence runs). Combined with P-synthesis-verify, this addresses the two genuinely new failure classes from cycle 19 and has clear leverage on workspace overhead.
