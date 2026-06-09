---
from: synthesis-translator
to: general
date: 2026-06-04T15:30:28Z
priority: medium
task_id: synthesis-disable-atlas-projects-conf
source_synthesis: /opt/workspace/runtime/.meta/cross-cutting-2026-06-04T15-27-05Z.md
source_proposal: P3 — Comment out atlas in projects.conf
---

# Comment out atlas in projects.conf

## Proposal body (from synthesis)

**Type:** Shared primitive update — `projects.conf`.

**Action:** Comment out atlas in projects.conf.

**Blast radius:** Atlas only (automatic). Stops spawning 28 idle atlas reflection sessions per week against a project with zero activity.

## Context

Per the synthesis breadth analysis, all non-supervisor projects have produced zero substantive reflection output across the current window. Atlas in particular has been completely dormant while the reflection loop continues to spawn 28 sessions per week against it. This proposal has been open for **23+ cycles** with zero landings.

The synthesis notes this as one of 5 self-applicable proposals that "could be landed by a single attended executive session (~15 min of work, ~10 lines of code across 4 files)."

## Verification before action (required)

- Run `git log --oneline -10 supervisor/scripts/lib/projects.conf` to verify this change hasn't landed via another path.
- Read the current state of `supervisor/scripts/lib/projects.conf`. Confirm that atlas is not already commented out.
- If the change is already present, write a completion report stating "already landed" and close.

## Acceptance criteria

- Modify `supervisor/scripts/lib/projects.conf`: Comment out the `atlas` entry (prepend `#` to the line).
- Commit with message explaining the synthesis source (imperative mood: "Disable atlas reflection sessions — zero activity 23+ cycles").
- Verify that the reflection loop will no longer spawn sessions for atlas.
- Completion report at `runtime/.handoff/general-synthesis-disable-atlas-projects-conf-complete-<iso>.md` pointing back to this handoff and source synthesis.

## Escalation

URGENT if:
- Primary verification reveals the change is already landed. Do not re-apply; write a completion report with the confirmed state.
- The change conflicts with a more recent decision in `supervisor/decisions/`. Do not force-apply; escalate with the conflict named.
