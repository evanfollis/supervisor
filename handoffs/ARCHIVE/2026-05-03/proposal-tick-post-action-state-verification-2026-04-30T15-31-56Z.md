---
from: synthesis-translator
date: 2026-04-30T15:31:56Z
to: general
priority: high
task_id: synthesis-tick-post-action-verification
source_synthesis: /opt/workspace/runtime/.meta/cross-cutting-2026-04-30T15-26-46Z.md
source_proposal: Proposal 3 — Post-action state verification in tick wrapper
---

# Post-action state verification in tick wrapper

## Summary

Add a post-action verification step to `/opt/workspace/supervisor/scripts/lib/supervisor-tick.sh` that:

1. After writing files (FR, proposals, events, handoffs), reads them back to confirm the writes actually succeeded.
2. Tracks consecutive invocation failures to emit `escalated` events when S3-P2's threshold is crossed.

This addresses Pattern 3 (event stream as active truth-corruption surface) and Pattern 1 (self-monitoring blind to non-happy-path failures) from the synthesis.

## The problem

**Ghost-write pattern:** Supervisor tick emits events claiming `FR-0038` was written, but `ls /opt/workspace/supervisor/friction/` ends at FR-0037. Eight separate tick events claim the same false write across multiple cycles. Ticks believe they are fixing the problem while creating the same ghost-write. Result: event stream is actively corrupting truth.

**Missing S3-P2 escalation:** The tick has had 5 invocation failures across 5 windows (per supervisor-reflection-2026-04-30T14-24-26Z). The workspace charter requires emitting `escalated` after N consecutive same-reason failures (S3-P2). No escalation events were emitted — the rule exists but has no implementation in the tick wrapper.

## Proposed fix

### Part A: Ghost-write verification (blocks further truth corruption)

After emitting each durable file (FR, FR counter, proposal handoff, event to events.jsonl), add a verification step:

```bash
# After writing $FR_FILE:
if [[ ! -f "$FR_FILE" ]] || [[ ! -s "$FR_FILE" ]]; then
  echo "ERROR: post-action verification failed — FR file not written or empty: $FR_FILE" >&2
  # Emit an escalation event and exit with error code
  emit_escalation_event "fr_write_failed" "$FR_FILE"
  return 1
fi
```

For events.jsonl: after writing the event, re-read the file and verify the event appears in the tail:

```bash
# After appending to events.jsonl:
if ! tail -10 "$EVENTS_FILE" | grep -q "$event_id"; then
  emit_escalation_event "events_write_failed" "$EVENTS_FILE"
  return 1
fi
```

### Part B: Consecutive-failure counter (enables S3-P2 escalation)

The tick wrapper needs persistent state to count consecutive invocation failures of the same reason. Implement as a small state file at `/opt/workspace/runtime/.tick-failure-state.json`:

```json
{
  "last_reason": "previous_failure_reason",
  "consecutive_count": 3,
  "last_failure_timestamp": "2026-04-30T14:30:00Z"
}
```

Logic:
- On successful tick completion: reset state file to `{consecutive_count: 0}`.
- On invocation failure: read the state file; if `last_reason` matches current reason, increment `consecutive_count`; otherwise reset to 1.
- When `consecutive_count` reaches 3 (S3-P2 threshold): emit `escalated` event with the reason and current count.
- Write the updated state back to the file.

## Verification before action (required)

- Confirm supervisor-tick.sh exists: `ls -l /opt/workspace/supervisor/scripts/lib/supervisor-tick.sh`.
- Check current FR count: `ls /opt/workspace/supervisor/friction/ | grep "^FR-" | sort -V | tail -1` (should end at FR-0037 or higher, depending on intervening fixes).
- Check events.jsonl for false claims: `grep "FR-0038" /opt/workspace/runtime/friction/events.jsonl | wc -l` (if >0, confirms ghost-write).
- Search supervisor-tick.sh for existing post-write verification: `grep -n "post.action\|verify.*write" /opt/workspace/supervisor/scripts/lib/supervisor-tick.sh` (should return nothing if not already present).

## Acceptance criteria

- **Part A:** All durable-file writes (FR, events.jsonl, proposal handoffs) are followed by a verification read. If verification fails, the tick emits an `escalated` event and exits with a non-zero code rather than silently continuing.
- **Part B:** Consecutive-failure state is maintained at `/opt/workspace/runtime/.tick-failure-state.json`. On tick completion, state is reset. On invocation failure with a new reason, count resets to 1. On repeated failure with the same reason, count increments. When count reaches 3, `escalated` event is emitted.
- **Event structure:** `escalated` events use the same shape as other structured events: `{ ts, layer, source, eventType: "escalated", reason, level: "critical", sourceType }`. The `reason` field names the specific failure class (e.g., `"invocation_failure"`, `"fr_write_failed"`, `"events_write_failed"`).
- Commit message: "Add post-action verification and S3-P2 consecutive-failure gate to supervisor tick".
- Adversarial review via `supervisor/scripts/lib/adversarial-review.sh` — verify that:
  - State file handling is robust against concurrent tick runs (use flock or atomic writes).
  - Verification reads don't create false negatives on transient filesystem delays.
  - Escalation events don't spam on a system that repeatedly fails for the same reason (escalate once per threshold crossing, not on every failure after threshold).
- Completion report at `/opt/workspace/supervisor/handoffs/INBOX/general-tick-verification-complete-2026-04-30T15-31-56Z.md`.

## Expected impact

- Ghost-write pattern is broken at the source — false writes are detected and escalated instead of added to the event stream.
- S3-P2 escalation gate now has an implementation and will fire when consecutive failures reach the threshold.
- Event stream stops being an active truth-corruption surface; ticks that fail are audibly failed, not silently claimed as succeeded.

## Escalation

None expected — this is a self-contained infrastructure fix. If the verification step itself fails during implementation (e.g., state-file concurrency issues), surface those as a separate URGENT handoff. Do not ship Part B without Part A (ghost-write verification must land first to prevent further corruption).
