---
from: synthesis-translator
to: general
date: 2026-05-20T15:32:51Z
priority: medium
task_id: synthesis-both-events-sync
source_synthesis: /opt/workspace/runtime/.meta/cross-cutting-2026-05-20T15-27-25Z.md
source_proposal: Proposal 6 (NEW, MEDIUM)
---

# Emit both synthesis_reviewed and delegated events in the same tick

**Status:** NEW diagnosis this cycle. Discovered in Pattern 2 (cycle 48 synthesis).

## Problem

The synthesis dispatch path is supposed to emit two events in sequence:
1. `synthesis_reviewed` — the executive acknowledges and reads a synthesis
2. `delegated` — the executive routes work from the synthesis to project/supervisor sessions

**Observed behavior:** The two events alternate cycles instead of both firing in the same tick.

- Cycle 46: `synthesis_reviewed` fired, `delegated` did not.
- Cycle 47: `delegated` fired, `synthesis_reviewed` did not.
- Cycle 48: Pattern continues (one or the other, not both).

This is a distinct failure from the ghost-write cascade (Pattern 2) and reflection cadence noise (Pattern 4). The dispatch logic is working (cycle 47 dispatch handoff exists at `runtime/.handoff/general-synthesis-cycle47-dispatch-2026-05-20T10-48Z.md`), but event accounting is incomplete.

## Proposal

File: `/opt/workspace/supervisor/scripts/lib/supervisor-tick.sh`

Add explicit sequential event emission in the synthesis dispatch path. After reading/acknowledging the synthesis, emit `synthesis_reviewed`. After writing dispatch handoff(s), emit `delegated`.

**Sketch of change:**

Find the section in `supervisor-tick.sh` that handles synthesis reading and handoff dispatch. Add two emit_event calls:

```bash
# After reading and acknowledging the synthesis:
emit_event "synthesis_reviewed" "acknowledged synthesis from cycle $SYNTHESIS_CYCLE" "$SYNTHESIS_REF"

# After writing each dispatch handoff:
emit_event "delegated" "routed proposal N to project $PROJECT" "$HANDOFF_REF"
```

Or, if dispatch is batched, emit once after all handoffs:

```bash
# After all dispatch handoffs are written:
emit_event "delegated" "routed $NUM_PROPOSALS from synthesis" "$DISPATCH_BATCH_REF"
```

**Rationale:** Event-model compliance gates. The supervision loop depends on both events firing to properly track synthesis → dispatch → execution flow. Missing one event causes meta-analysis to misclassify cycles as "no dispatch" when dispatch actually happened.

**Blast radius:** Supervisor tick only (automatic). No side effects on project repos or other systems.

## Evidence

Cycles 46–48: Synthesis dispatch path verified as functional (cycle 47 handoff exists on disk with correct content). But event logs show only one of the two required events per cycle. Meta-analysis (supervisor reflection, synthesis synthesis) uses event model to classify cycle state — missing events cause misclassification.

Supervisor reflection (14:26Z, cycle 48, O3): "Event-sequence inversion between cycles. Cycle 46: `synthesis_reviewed` fired, `delegated` did not. Cycle 47: `delegated` fired, `synthesis_reviewed` did not. The two required event types alternate rather than both firing in the same tick."

## Verification before action (required)

- Read `/opt/workspace/supervisor/scripts/lib/supervisor-tick.sh` and search for `emit_event` calls. Count how many emit `synthesis_reviewed` and how many emit `delegated`.
- Check `supervisor/events/supervisor-events.jsonl`. Tail the last 50 lines. Count the last few cycles: how many have both `synthesis_reviewed` and `delegated` in the same day/tick?
- If both events are already being emitted in sync, write a completion report saying "already landed — both events firing at lines <N> and <M>" rather than re-applying.

## Acceptance criteria

- `supervisor-tick.sh` updated to emit `synthesis_reviewed` event after reading the synthesis.
- `supervisor-tick.sh` updated to emit `delegated` event after writing dispatch handoff(s).
- Both events fire in the same supervisor-tick run (same tick output timestamp).
- Events are logged to `supervisor/events/supervisor-events.jsonl` with proper JSON format.
- A complete tick run produces both events visible in the event log.
- Completion report at `supervisor/handoffs/INBOX/general-both-events-sync-complete-<iso>.md` showing sample events from the fixed tick.

## Escalation

URGENT if:
- `supervisor-tick.sh` does not use `emit_event` function or has a different event-logging mechanism. Identify the actual logging path and propose the amendment there.
- The dispatch path is split across multiple scripts (e.g. synthesis dispatch in synthesize.sh, handoff routing in dispatcher.sh). If so, identify which script should emit which event and coordinate the amendment across both.
