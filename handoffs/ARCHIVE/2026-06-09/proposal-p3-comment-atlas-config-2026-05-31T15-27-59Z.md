---
from: synthesis-translator
to: general
date: 2026-05-31T15:27:59Z
priority: high
task_id: synthesis-p3-comment-atlas-config
source_synthesis: /opt/workspace/runtime/.meta/cross-cutting-2026-05-31T15-23-50Z.md
source_proposal: P3 — Comment out atlas in projects.conf
---

# P3 — Comment out atlas in projects.conf

**Type**: Config edit — `supervisor/scripts/lib/projects.conf`

**Change**: Comment out the `atlas|/opt/workspace/projects/atlas` line (line 15).

**Blast radius**: Atlas only. Stops 4 idle reflection sessions/day (28/week). No project activity in atlas for 15+ consecutive cycles.

**Rationale**: Atlas has produced no substantive reflection activity for 15+ cycles. The reflection loop is running 16 sessions/day against zero active projects, producing diminishing-returns diagnostic output. Removing atlas from the loop reduces unnecessary overhead without losing signal quality — if atlas activity resumes, it can be re-enabled.

## Verification before action (required)

- Run `git log --oneline -5` on `supervisor/`. Check if this line has already been commented out.
- Read `supervisor/scripts/lib/projects.conf` line 15. Verify it still shows `atlas|/opt/workspace/projects/atlas` (uncommented).
- If either check shows this is already applied, write a completion report stating "already landed" rather than re-applying.

## Acceptance criteria

- Line 15 in `projects.conf` is now commented out (prefix with `#`).
- Change committed with clear message explaining the synthesis source and the rationale (15+ cycles of no activity).
- Completion report at `runtime/.handoff/general-supervisor-synthesis-p3-complete-<iso>.md` pointing back to this handoff.

## Escalation

URGENT if:
- Primary verification reveals this line has already been commented out. Write a brief completion report saying "already landed" and close.
- There is a recent decision in `supervisor/decisions/` that contradicts this proposal (e.g., a directive to keep atlas in the loop). Escalate with the conflict named.
