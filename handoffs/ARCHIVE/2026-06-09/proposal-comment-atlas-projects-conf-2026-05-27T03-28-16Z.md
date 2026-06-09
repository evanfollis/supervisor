---
from: synthesis-translator
to: general
date: 2026-05-27T03:28:16Z
priority: high
task_id: synthesis-comment-atlas-reflection
source_synthesis: /opt/workspace/runtime/.meta/cross-cutting-2026-05-27T03-24-35Z.md
source_proposal: Proposal 3 — Comment out atlas in projects.conf
---

# Comment out atlas in projects.conf

## Summary

Atlas is a parked project (per ADR-0033) with the runner stopped for 9 days. The reflection loop has produced 30 consecutive idle cycles, each generating structurally identical "nothing changed" reports. This consumes ~360 agent-hours of reflection capacity and adds noise to the INBOX count (+5 items). The fix is a single-line config change: comment out the atlas entry in the reflection loop.

## What to do

Edit `supervisor/scripts/lib/projects.conf` and comment out the atlas line:

Change:
```
atlas|/opt/workspace/projects/atlas
```

To:
```
# atlas|/opt/workspace/projects/atlas  # Parked per ADR-0033; re-enable when Shape 4 work begins
```

This removes atlas from the 12-hour reflection loop while preserving the line for future re-enablement.

## Why this matters

Concrete cost:
- 30 idle cycles × ~12 agent-hours per reflection = 360 agent-hours of idle polling
- Each cycle generates API token consumption and a structurally identical report
- The URGENT for this change (in `runtime/.handoff/`) has been open >25 hours

The information value of reflecting on a parked project is zero. This is mechanical waste, not a strategic decision pending input.

## Verification before action (required)

- Confirm atlas is parked: `cat /opt/workspace/supervisor/decisions/0033-*.md` or similar, confirm ADR-0033 exists and names atlas parked status
- Confirm atlas runner is stopped: Check the most recent atlas-reflection-*.md files — they should all show "no changes detected; entry idle count N"
- If either is false, report the actual state and don't apply the patch

## Acceptance criteria

- `projects.conf` has the atlas line commented out with a clear comment
- Change committed with message citing the synthesis and the parked status
- Verify: `grep "^atlas" projects.conf` returns nothing
- Next 12h reflection cycle should skip atlas entirely (check the window table at the top of the next cross-cutting synthesis)

## No adversarial review needed

This is a config opt-out. No logic, no risk.

## Escalation

URGENT if:
- Atlas is no longer parked per principal update — revert and update the comment
- Recent commits show Shape 4 work has begun — revert and leave atlas in the loop
