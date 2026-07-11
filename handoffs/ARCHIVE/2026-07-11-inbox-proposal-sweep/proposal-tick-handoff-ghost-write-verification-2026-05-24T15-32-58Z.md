---
from: synthesis-translator
to: general
date: 2026-05-24T15:32:58Z
priority: high
task_id: synthesis-tick-ghost-write-fix
source_synthesis: /opt/workspace/runtime/.meta/cross-cutting-2026-05-24T15-26-05Z.md
source_proposal: Proposal 2 — Pre-emit verification in tick event logging
---

# Proposal 2: Pre-emit verification in tick event logging

**Problem statement**: The ghost-write pattern has recurred for the 5th+ window. The cycle-55 dispatch handoff was claimed at 04:47Z but not actually created until 08:49Z. Each occurrence produces a false audit trail. The fix is straightforward: before a tick emits a `delegated` or `handoff_received` event claiming a file was created/processed, verify the file exists first.

**Type:** Shared primitive fix (`supervisor-tick.sh`).

**What:** Before a tick emits a `delegated` or `handoff_received` event claiming a file was created/processed, verify the file exists. If it doesn't, emit `handoff_ghost_write` instead of the claiming event, and create the file in the next tick (or defer to next run).

**Why:** The ghost-write pattern has recurred for the 5th+ window (cycle-55 dispatch handoff was claimed at 04:47Z but not created until 08:49Z). Each occurrence produces a false audit trail. A pre-emit file existence check eliminates the class entirely.

**Blast radius:** Supervisor tick only (automatic). No effect on reflections or attended sessions. Affects only the event log accuracy; no behavioral change to the tick itself.

**Reference implementation sketch:**
```bash
# Before emitting 'delegated' for a handoff file:
_emit_delegated() {
  local handoff_path="$1"
  local event_note="$2"
  
  if [[ ! -f "$handoff_path" ]]; then
    _emit_event "handoff_ghost_write" "$handoff_path" \
      "Tick attempted to emit delegated event but file does not exist; deferring to next tick"
    return 1
  fi
  
  _emit_event "delegated" "$handoff_path" "$event_note"
  return 0
}

# Usage in supervisor-tick.sh:
# _emit_delegated "/opt/workspace/runtime/.handoff/project-name-*.md" "delegated to project session"
```

## Verification before action (required)

- [ ] Check if this has already landed in `supervisor/scripts/lib/supervisor-tick.sh` by searching for `handoff_ghost_write` or similar ghost-write detection logic. If present, write completion report "already landed" with the commit hash.
- [ ] If not landed: read the current `supervisor/scripts/lib/supervisor-tick.sh` emit_event function and the places where `delegated` events are emitted to understand the call sites.
- [ ] Confirm that the ghost-write problem is still occurring by checking `supervisor-events.jsonl` for recent `delegated` events that reference non-existent files.

## Acceptance criteria

- The tick includes a pre-emit file existence check before emitting `delegated` or `handoff_received` events.
- If a file doesn't exist when claimed, the tick emits `handoff_ghost_write` instead of claiming the event.
- The implementation covers all call sites where the tick claims to have created or processed a handoff.
- Committed with message: "Fix: add pre-emit file verification for handoff events to prevent ghost-writes"
- No adversarial review needed for this fix (it is a straightforward defensive pattern addition).

## Escalation

URGENT if:
- The proposal has already landed via another path. Write completion report: "already landed at commit <SHA>" and close.
- The supervisor-tick.sh emit_event function has been significantly refactored, making the implementation approach unclear. Escalate with the current function signature so principal can clarify approach.
