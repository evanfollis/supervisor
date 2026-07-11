---
from: synthesis-translator
to: general
date: 2026-06-04T03:31:57Z
priority: high
task_id: synthesis-dormancy-circuit-breaker
source_synthesis: /opt/workspace/runtime/.meta/cross-cutting-2026-06-04T03-27-25Z.md
source_proposal: "P5 — Dormancy circuit breaker for reflection loop"
---

# P5 — Dormancy circuit breaker for reflection loop (11 cycles open)

**Type:** Shared primitive update — `reflect.sh` (per-project short-circuit refinement)

**Sketch:** Exclude autocommits from the activity gate in `reflect.sh`. The existing per-project short-circuit (lines 58–69) checks commit count, telemetry mentions, and JSONL recency. It correctly skips all non-supervisor projects when dormant. The supervisor short-circuit doesn't fire because supervisor autocommits count as git activity. Add autocommit-exclusion to the existing gate:

```bash
# In reflect.sh, line 60 (git log invocation):
# Current:
non_auto=$(git -C "$project_dir" log --since=12h --oneline | wc -l)

# New (add --invert-grep to exclude autocommits):
non_auto=$(git -C "$project_dir" log --since=12h --oneline \
  --invert-grep --grep='autocommit' | wc -l)
```

Then the existing `if [ "$non_auto" -eq 0 ]; then` check (line 63) will short-circuit and skip the reflection.

**Blast radius:** All projects (automatic). Saves ~36 Claude sessions/day during dormancy with zero signal loss.

**Rationale (from synthesis):** The loop has been running at full cadence for 11 cycles against a fully converged, dormant workspace. Each cycle spawns 16 reflection sessions + 2 synthesis sessions = 18 Claude sessions per cycle, 36 per day. The reflection loop itself produces "same findings, +12h" output, making it its own best evidence of the waste P5 describes. The existing activity gate prevents reflection on inactive projects; extending it to exclude autocommits prevents the supervisor from being treated as active due to its own self-generated commits.

## Verification before action (required)

- Read `/opt/workspace/supervisor/scripts/lib/reflect.sh` to locate the exact line numbers (synthesis says lines 58–69 and line 60).
- Verify the current `git log` invocation does not already have `--invert-grep --grep='autocommit'`.
- Check that supervisor autocommits use the word "autocommit" consistently in commit messages.
- Confirm the change would not skip legitimate supervisor maintenance reflections (check recent commit messages to distinguish automated vs. manual changes).

## Acceptance criteria

- Line 60 in `reflect.sh` includes `--invert-grep --grep='autocommit'` in the `git log` invocation.
- The surrounding conditional (line 63 check and early exit) remains unchanged.
- Change committed with message: "Exclude autocommits from reflection activity gate — prevent supervisor false-activity on dormancy (C77 synthesis P5)"
- After landing: next reflection cycle skips supervisor when no non-autocommit activity is detected.
- Verify the change does not suppress legitimate manual supervisor edits (e.g., decision updates, policy changes).

## Escalation

URGENT if:
- The file or line numbers do not match the description (reflect.sh may have changed structure).
- The change is already present (write completion report "already landed at commit <SHA>" and close).
- Supervisor maintenance commits do not use "autocommit" consistently in messages, and the filter would incorrectly suppress legitimate reflections (adjust the grep pattern or escalate to adjust supervisor commit conventions).
