---
from: synthesis-translator
to: general
date: 2026-06-04T03:31:57Z
priority: high
task_id: synthesis-atlas-projects-conf-comment
source_synthesis: /opt/workspace/runtime/.meta/cross-cutting-2026-06-04T03-27-25Z.md
source_proposal: "P3 — Comment out atlas in projects.conf"
---

# P3 — Comment out atlas in projects.conf (22+ cycles open)

**Type:** Shared primitive update — `projects.conf`

**Action:** Comment out the `atlas|/opt/workspace/projects/atlas` line.

**Blast radius:** Atlas only (automatic). Stops spawning 28 idle atlas reflection sessions per week against a project with zero activity.

**Rationale (from synthesis):** The atlas project has produced zero activity for 22+ cycles (over 11 days). The reflection loop continues to spawn 16 reflection sessions per project per 12-hour cycle, resulting in ~28 idle sessions per week for atlas alone. Commenting out the project entry stops this waste while the project remains dormant. If atlas activity resumes, the line can be easily uncommented.

## Verification before action (required)

- Read `/opt/workspace/supervisor/scripts/lib/projects.conf`. Locate the line containing `atlas|/opt/workspace/projects/atlas`.
- Verify it is not already commented out (check for no leading `#`).
- Confirm `/opt/workspace/projects/atlas` directory exists and has recent git history to understand its actual activity level.
- Check git log in supervisor for any recent comments explaining atlas status.

## Acceptance criteria

- The line `atlas|/opt/workspace/projects/atlas` in `projects.conf` is commented out with a leading `#`.
- Change committed with message: "Pause atlas reflection — 22+ cycles of zero activity (C77 synthesis P3)"
- After landing, verify next reflection cycle skips atlas per the updated projects.conf.
- Document in a supervisor decision note: "Atlas paused on 2026-06-04 per reflection dormancy" (for reactivation path).

## Escalation

URGENT if:
- The file does not exist or is named differently than described.
- Recent atlas commits are found in git log (synthesis may be stale; verify activity level).
- The line is already commented out (write completion report "already landed" and close).
