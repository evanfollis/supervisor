---
from: synthesis-translator
to: general
date: 2026-06-05T15:29:43Z
priority: high
task_id: synthesis-dormancy-circuit-breaker
source_synthesis: /opt/workspace/runtime/.meta/cross-cutting-2026-06-05T15-26-05Z.md
source_proposal: P5 — Dormancy circuit breaker for reflection loop (14 cycles open)
---

# P5 — Dormancy circuit breaker for reflection loop

**Type:** Shared primitive update — 1-line change to `reflect.sh`.

**Pattern:** Reflection/synthesis loop running at full cadence against converged workspace (14 cycles). Each cycle spawns ~18 Claude sessions to produce structurally identical output. Over 14 breadth-deficit cycles (~7 days), ~252 Claude sessions producing ~98KB of convergent diagnosis.

**Failure class:** Fixed-cadence automation with no dormancy circuit breaker.

**Proposed change:**
```bash
non_auto=$(git -C "$project_dir" log --since="${WINDOW_HOURS}h" --oneline \
  --invert-grep --grep='autocommit' | wc -l)
if [ "$non_auto" -eq 0 ]; then echo "# Reflection skipped"; exit 0; fi
```

Add this check to `reflect.sh` so that when a project has zero non-autocommit activity in the reflection window, reflection exits early rather than running full analysis on unchanged state.

**Blast radius:** All projects (automatic). Saves ~36 Claude sessions/day during dormancy. Currently 252 wasted sessions across 14 dormant cycles.

**Evidence:** Cycle 20 (summary): "This cycle is structurally identical to cycles 11-19." Each cycle produces the same diagnosis without new material. The loop has been in dormant state since C66 with no circuit breaker.

## Verification before action (required)

- Read `/opt/workspace/supervisor/scripts/lib/reflect.sh` to confirm the current structure and where to add the check
- Verify this change has not already landed (check recent commits and file state)
- If already landed, write completion report noting "already landed at commit <SHA>" and exit

## Acceptance criteria

- The dormancy check is added to `reflect.sh` before the main reflection logic runs
- A project with zero non-autocommit activity in the window exits with early exit message
- Commit message explains the synthesis source and the pattern it addresses (14 cycles of wasted sessions during dormancy)
- Completion report at `/opt/workspace/runtime/.handoff/general-synthesis-dormancy-circuit-breaker-complete-<iso>.md` pointing back to this handoff and source synthesis

## Escalation

URGENT if:
- Verification reveals this check has already landed by another path — write brief completion saying "obsolete — already landed" and close
- The reflect.sh structure has changed significantly since C80 synthesis — surface the structural mismatch and request clarification
