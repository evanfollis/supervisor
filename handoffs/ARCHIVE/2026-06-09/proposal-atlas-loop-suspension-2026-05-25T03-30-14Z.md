---
from: synthesis-translator
to: general
date: 2026-05-25T03:30:14Z
priority: high
task_id: synthesis-atlas-loop-suspension
source_synthesis: /opt/workspace/runtime/.meta/cross-cutting-2026-05-25T03-24-49Z.md
source_proposal: Proposal 2 (CONCRETE — cadence reduction)
---

# Suspend atlas from 12h reflection loop

**Type:** Shared primitive config (`projects.conf`).

**What:** Comment out or remove the atlas line in `/opt/workspace/supervisor/scripts/lib/projects.conf`. Re-enable when `systemctl start atlas-runner.service` is executed.

**Why:** 26 consecutive idle reflection cycles. Each produces a near-duplicate file, consumes tokens, and generates zero actionable signal. The atlas reflection itself has proposed this for 3+ cycles (since cycle 24). Runner has been STOPPED since 2026-05-18. All atlas work is blocked on principal input (ADR-0033 sign-off + Shape 4 alt-data source).

**Blast radius:** Atlas only (opt-in to re-enable). Saves ~2 reflection sessions/day and their downstream synthesis bandwidth.

**Sketch:**
```
# In projects.conf, change:
atlas|/opt/workspace/projects/atlas
# to:
# atlas|/opt/workspace/projects/atlas  # suspended: runner STOPPED since 2026-05-18, 26 idle cycles
```

## Verification before action (required)

- Check `/opt/workspace/supervisor/scripts/lib/projects.conf` line 15. Verify the atlas line is currently uncommented.
- Confirm `systemctl is-active atlas-runner.service` shows inactive/stopped.
- If either differs from the proposal context, escalate with the current state.

## Acceptance criteria

- The atlas line in projects.conf is commented out with the reasoning noted.
- Change committed with clear message explaining why atlas reflection is temporarily suspended.
- Next reflection cycle skip count confirms atlas is no longer included.

## Escalation

URGENT if:
- The atlas runner service has been restarted between the synthesis write (03:24Z) and this handoff application. If restarted, verify with the principal whether the suspension should still apply.
