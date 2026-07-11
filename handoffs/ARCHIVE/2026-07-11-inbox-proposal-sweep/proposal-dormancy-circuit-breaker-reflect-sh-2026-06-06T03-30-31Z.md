---
from: synthesis-translator
to: general
date: 2026-06-06T03:30:31Z
priority: high
task_id: synthesis-dormancy-circuit-breaker
source_synthesis: /opt/workspace/runtime/.meta/cross-cutting-2026-06-06T03-25-20Z.md
source_proposal: "P5 — Dormancy circuit breaker for reflection loop (15 cycles open)"
---

# P5 — Dormancy circuit breaker for reflection loop

**Type:** Shared primitive update — `reflect.sh`.

Move the inactivity check before session spawn, not inside it. Currently the check happens inside a Claude session that costs tokens; it should happen in bash before the session starts.

**Sketch:**
```bash
# In reflect.sh, before spawning the Claude session:
non_auto=$(git -C "$project_dir" log --since="${WINDOW_HOURS}h" --oneline \
  --invert-grep --grep='autocommit' | wc -l)
if [ "$non_auto" -eq 0 ]; then
  echo "# Reflection skipped — no activity" > "$output_file"
  exit 0
fi
```

**Blast radius:** All projects (automatic). Eliminates ~14 wasted Claude sessions per cycle during dormancy. Currently ~270 wasted sessions over 15 cycles.

**Context:** Cycle 21 diagnosis states this has been the dominant waste source during the 15-cycle breadth deficit. Moving the check from inside the Claude session to pre-spawn in bash prevents token burn on dormancy runs.

## Verification before action (required)

- Check current state of `/opt/workspace/supervisor/scripts/lib/reflect.sh` to see where the inactivity check currently lives
- Confirm the check is inside the spawned Claude session, not before it

## Acceptance criteria

- The inactivity check (git log --since + grep for non-autocommit activity) is moved to bash, before `codex exec` / Claude session spawn
- If no non-autocommit activity in the window, the script writes a skipped output file and exits with status 0
- Change committed with message explaining the synthesis source and the cycle counts (270 wasted sessions over 15 cycles)
- Spot-check on one project to verify reflect.sh produces a skipped file without spawning a session during dormancy

## Escalation

URGENT if:
- The inactivity check has already been moved in a recent commit. Report "already landed at commit <SHA>" and close.
- The check would need to be applied differently for some projects. Surface the constraint with examples.
