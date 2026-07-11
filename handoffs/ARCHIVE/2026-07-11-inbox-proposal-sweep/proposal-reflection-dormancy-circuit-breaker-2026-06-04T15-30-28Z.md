---
from: synthesis-translator
to: general
date: 2026-06-04T15:30:28Z
priority: high
task_id: synthesis-reflection-dormancy-circuit-breaker
source_synthesis: /opt/workspace/runtime/.meta/cross-cutting-2026-06-04T15-27-05Z.md
source_proposal: P5 — Dormancy circuit breaker for reflection loop
---

# Dormancy circuit breaker for reflection loop

## Proposal body (from synthesis)

**Type:** Shared primitive update — 1-line change to the `git log` invocation in `reflect.sh` line ~60.

**Sketch:**
```bash
# In reflect.sh, modify the commit-count check to exclude autocommits:
non_auto=$(git -C "$project_dir" log --since="${WINDOW_HOURS}h" --oneline \
  --invert-grep --grep='autocommit' | wc -l)
```

**Blast radius:** All projects (automatic). Saves ~36 Claude sessions/day during dormancy with zero signal loss. The existing per-project short-circuit already fires for all non-supervisor projects — this change would make it fire for supervisor too when the only activity is autocommits.

## Context

The reflection/synthesis loop has been converged (producing structurally identical output) for 12 consecutive cycles. The loop continues to run at full cadence, spawning 16 reflection sessions + 2 synthesis sessions = 18 Claude sessions per cycle, 36 per day. Over the past 6 days of dormancy, this has produced ~216 Claude sessions and ~84KB of "same as last time, +12h" output.

This is the exact waste this proposal describes — the loop is its own most obvious evidence of what it proposes to fix.

The synthesis notes this as one of 5 self-applicable proposals that "could be landed by a single attended executive session (~15 min of work, ~10 lines of code across 4 files)." This proposal has been open for **9 cycles** with zero landings.

## Verification before action (required)

- Run `git log --oneline -10 supervisor/scripts/lib/reflect.sh` to verify this change hasn't landed via another path.
- Read the current state of `supervisor/scripts/lib/reflect.sh` around line 60. Confirm the commit-count check does not yet use `--invert-grep --grep='autocommit'`.
- If the change is already present, write a completion report stating "already landed" and close.

## Acceptance criteria

- Modify `supervisor/scripts/lib/reflect.sh` at line ~60:
  - Change the `git log` invocation to exclude autocommit-only activity using `--invert-grep --grep='autocommit'`.
  - Example: `non_auto=$(git -C "$project_dir" log --since="${WINDOW_HOURS}h" --oneline --invert-grep --grep='autocommit' | wc -l)`
- Commit with message explaining the synthesis source (imperative mood: "Add dormancy circuit breaker to reflection loop — skip when only autocommits").
- Test with supervisor's recent history (should fire short-circuit on next reflection cycle).
- Completion report at `runtime/.handoff/general-synthesis-reflection-dormancy-circuit-breaker-complete-<iso>.md` pointing back to this handoff and source synthesis.

## Escalation

URGENT if:
- Primary verification reveals the change is already landed. Do not re-apply; write a completion report with the confirmed state.
- The change conflicts with a more recent decision in `supervisor/decisions/`. Do not force-apply; escalate with the conflict named.
