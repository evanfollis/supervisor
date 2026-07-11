---
from: synthesis-translator
to: general
date: 2026-05-15T15:27:59Z
priority: high
task_id: synthesis-event-integrity-gate
source_synthesis: /opt/workspace/runtime/.meta/cross-cutting-2026-05-15T15-23-27Z.md
source_proposal: Proposal 1 — Event integrity gate for tick event emission
---

# Event integrity gate for tick event emission

**Type:** Shared primitive change — `supervisor-tick.sh` or the tick's event emission helper.

**Purpose:** Prevent `friction_filed` (and similar materialization-claiming events) from being emitted for files that exist only on tick branches, not on main.

## Problem statement

The ghost-write cascade (standing since cycle 28) has crossed a threshold: it is no longer just failing to land files on main — it is actively corrupting the event stream that downstream consumers (synthesis, meta-scan, attended reentry) treat as truth.

**Evidence:**
- Supervisor event log contains 8+ `friction_filed` events for FR-0042 and FR-0043 that have never materialized on main
- Verified: `git show main:friction/FR-0042-*` returns `fatal: path does not exist in 'main'`
- At least 4 tick branches contain the file; main does not
- The event stream claims materialization that hasn't occurred on the canonical surface

Any consumer that reads events without cross-checking main gets false positives. False events are strictly worse than ghost-writes — ghost-writes are silent non-delivery; false events are active misinformation.

## Implementation

**5-line sketch:**

```bash
emit_friction_event() {
  local fr_path="$1"
  if git show "main:${fr_path}" >/dev/null 2>&1; then
    emit_event "friction_filed" "$fr_path"
  else
    emit_event "friction_blocked" "$fr_path" "branch-only, pending merge"
  fi
}
```

**Scope:** Supervisor tick sessions only (automatic). No project impact. Immediately stops false event accumulation.

## Verification before action (required)

- Run `git log --oneline -20` in `/opt/workspace/supervisor`. Check if this event gate has already landed via another path.
- Read `/opt/workspace/supervisor/scripts/lib/supervisor-tick.sh`. Check if `emit_friction_event` or similar integrity checks are already present.
- If either is true, write a completion report stating "already landed at commit <SHA> / verified in-file" rather than re-applying.

## Acceptance criteria

- The event integrity gate is implemented in supervisor-tick.sh (or relevant event emission helper)
- `friction_filed` events are only emitted when the file exists on `HEAD` of main
- `friction_blocked` events are emitted instead when files exist only on tick branches
- Change committed with clear message: "Add event integrity gate to prevent false materialization events"
- No adversarial review required (focused code fix, minimal scope)
- Completion report at `runtime/.handoff/general-supervisor-synthesis-event-integrity-gate-complete-<iso>.md` pointing back to this handoff and the source synthesis

## Escalation

URGENT if:
- Primary verification reveals this has already landed by another path. Close with "obsolete — already landed."
- The event-stream corruption pattern persists after landing. Escalate with new evidence.
