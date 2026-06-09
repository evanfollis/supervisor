---
from: synthesis-translator
to: general
date: 2026-06-03T15:26:00Z
priority: high
task_id: synthesis-p3-atlas-projects-conf
source_synthesis: /opt/workspace/runtime/.meta/cross-cutting-2026-06-03T15-23-08Z.md
source_proposal: P3 — Comment out atlas in projects.conf (20+ cycles open)
---

# P3 — Comment out atlas in projects.conf

**Type:** Shared primitive update — `projects.conf`.

**Action:** Comment out the atlas line in `projects.conf`.

**Blast radius:** Atlas only (automatic). Stops spawning 28 idle atlas reflection sessions per week against a project with zero activity.

**Rationale:** The reflection/synthesis loop has been running against a dormant workspace for 10+ cycles. Atlas has shown zero activity, yet the loop spawns 28 idle reflection sessions per week against it. Commenting out the atlas line eliminates this wasted compute without blocking the project if it becomes active again.

## Verification before action (required)

- Read `/opt/workspace/supervisor/scripts/lib/projects.conf` and check if the atlas line is already commented out.
- If already commented, write a completion report stating "already commented in projects.conf" rather than re-applying.

## Acceptance criteria

- The atlas entry in `projects.conf` is commented out (prefixed with `#`).
- Change committed with message: "Comment out atlas in projects.conf; halt idle reflection sessions (synthesis P3)"
- No additional review needed — straightforward configuration change.
- Completion report at `runtime/.handoff/general-supervisor-synthesis-p3-complete-<iso>.md` pointing back to this handoff and the source synthesis.

## Escalation

URGENT if:
- The line is already commented — verify in-file and close.
- Atlas becomes active (commits appear) before this lands — defer and notify principal.
