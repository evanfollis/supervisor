---
from: synthesis-translator
to: general
date: 2026-06-28T15:32:45Z
priority: high
task_id: synthesis-p7-reflect-failure
source_synthesis: /opt/workspace/runtime/.meta/cross-cutting-2026-06-28T15-27-10Z.md
source_proposal: P7 (CRITICAL, carry from C110 — 3rd cycle)
---

# Reflection failure self-reporting (P7)

## Full proposal from synthesis

**Status:** Not implemented. `reflect.sh:115-119` still exits with code 2
and stderr warning only. No handoff written, no telemetry event emitted.

**Sketch unchanged from C110/C111.** Independent of all other proposals.
<5 min effort. The 7-day blind period (Pattern 6) demonstrated the failure
class this prevents.

**Blast radius:** All reflected projects (automatic — fires on failure).

## Verification before action (required)

- Verified: `reflect.sh` lines 115-119 currently show:
  ```bash
  if [[ -f "$OUTPUT_FILE" ]]; then
    echo "reflect[$PROJECT]: wrote $OUTPUT_FILE"
  else
    echo "reflect[$PROJECT]: WARNING — no output file produced" >&2
    exit 2
  fi
  ```
- Behavior: exits with code 2 and warning message only. No handoff. No event emitted.
- This is the missing P7 implementation.

## Acceptance criteria

- When reflect.sh exits with code 2 (no output file produced):
  - Write a handoff to `supervisor/handoffs/INBOX/` naming the project and failure reason.
  - Emit a telemetry event of type `escalated` with the event class name.
  - Exit with code 2 still (do not hide the failure).
- Change committed with message explaining the self-reporting addition.
- Adversarial review via `supervisor/scripts/lib/adversarial-review.sh` recommended for non-trivial prompt/event-shape changes.
- Completion report filed at `runtime/.handoff/general-claude-synthesis-p7-reflect-failure-complete-<iso>.md`.

## Escalation

None expected. This is a defensive patch to catch silent failures in the reflection loop.

### Context: why this matters

The 7-day blind period (C105-C110, synthesis cycle Pattern 6) demonstrated that when reflection fails silently (exit 2, warning only), the synthesis loop has no signal that projects are not being observed. Synthesis proposals continue to reference old state, and the executive has false confidence in coverage. A handoff + event makes the failure visible to the executive so it can be addressed within 24h per dispatch obligations (CLAUDE.md §Automated Self-Reflection Loop).
