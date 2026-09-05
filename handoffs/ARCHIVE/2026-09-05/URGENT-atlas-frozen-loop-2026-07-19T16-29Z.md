---
priority: critical
created: 2026-07-19T16:29:40.345243+00:00
from: atlas.runner (self-emitted via S3-P2 escalation gate)
to: atlas / general
---

# atlas — frozen loop (auto-escalated)

The autonomous loop has produced 863 consecutive
all-continue cycles with no kill/promote/pivot decisions.
Evidence store size: 293.

## Likely causes

- Dataset retest cache is too aggressive (DATASET_RETEST_AFTER) —
  hypothesis is being re-evaluated against the same evidence.
- All available data has been exhausted under the current signal
  detectors; new detectors or new data sources needed.
- A bug is silently dropping experiment runs.

## Diagnostic

  grep '"eventType": "cycle.completed"' \
    /opt/workspace/runtime/.telemetry/events.jsonl | tail -10
  .venv/bin/atlas strategy readiness

Delete this file once the root cause is addressed; the gate is
idempotent and will re-fire only on a new streak.
