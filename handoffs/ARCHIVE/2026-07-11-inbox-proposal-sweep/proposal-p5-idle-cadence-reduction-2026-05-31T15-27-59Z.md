---
from: synthesis-translator
to: general
date: 2026-05-31T15:27:59Z
priority: high
task_id: synthesis-p5-idle-cadence-reduction
source_synthesis: /opt/workspace/runtime/.meta/cross-cutting-2026-05-31T15-23-50Z.md
source_proposal: P5 — Idle-period cadence reduction for reflection/synthesis
---

# P5 — Idle-period cadence reduction for reflection/synthesis

**Type**: Shared primitive edit — `reflect-all.sh` or `reflect.sh`

**Sketch**: Before spawning per-project reflection sessions, check a dormancy signal (e.g., no attended session in 48h AND all prior-cycle reflections were skipped). If dormant, run supervisor-only reflection and skip the 7 dormant projects. The synthesis job runs only if at least 2 non-skipped reflections exist with substantive content.

Proposed code (in reflect-all.sh, before the project loop):
```bash
# In reflect-all.sh, before the project loop:
DORMANT_THRESHOLD=172800  # 48h
last_attended=$(stat -c %Y "$RUNTIME_ROOT/.last-attended-session" 2>/dev/null || echo 0)
now=$(date +%s)
if (( now - last_attended > DORMANT_THRESHOLD )); then
  # Only reflect on supervisor; skip dormant projects
  PROJECTS=("supervisor|$SUPERVISOR_ROOT|reflect-supervisor-prompt.md")
fi
```

**Blast radius**: All projects (but only during dormancy — no effect when workspace is active). Saves ~28 idle reflection sessions/day during dormant periods. Automatic.

**Rationale**: The workspace is running its full observability stack — 16 reflection sessions/day, 2 synthesis sessions/day — against zero project activity. The loop correctly identifies problems but has no circuit breaker for "I have converged and no one is listening." This reduces the loop's own cost during dormancy without losing signal quality when the workspace reactivates.

## Verification before action (required)

- Run `git log --oneline -10` on `supervisor/`. Check if dormancy-reduction logic has already landed.
- Look for the file `supervisor/scripts/lib/reflect-all.sh`. If it exists, check for dormancy logic. If it doesn't exist, check `supervisor/scripts/lib/reflect.sh` for similar logic.
- If either check shows this is already applied, write a completion report stating "already landed" rather than re-applying.

## Acceptance criteria

- A dormancy detection mechanism is now in place that reduces reflection/synthesis cadence during dormant periods (no attended session for 48h+).
- The mechanism runs supervisor-only reflection during dormancy and skips dormant projects.
- The synthesis job runs only if at least 2 non-skipped reflections exist with substantive content.
- Change committed with clear message explaining the synthesis source and the rationale.
- Completion report at `runtime/.handoff/general-supervisor-synthesis-p5-complete-<iso>.md` pointing back to this handoff.

## Escalation

URGENT if:
- Primary verification reveals this logic has already landed by another path. Write a brief completion report saying "already landed" and close.
- The change requires more extensive refactoring than the sketch proposed (e.g., refactoring reflect.sh to split concerns). Escalate with the specific technical blockers and propose a revised scope.
