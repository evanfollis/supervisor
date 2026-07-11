---
from: synthesis-translator
to: general
date: 2026-06-10T03:31:35Z
priority: high
task_id: synthesis-p-skip-escalation
source_synthesis: /opt/workspace/runtime/.meta/cross-cutting-2026-06-10T03-23-06Z.md
source_proposal: "Proposal 2: P-skip-escalation — Add consecutive-skip counter and escalation to reflect.sh"
---

# P-skip-escalation — Add consecutive-skip counter and escalation to reflect.sh

**Type:** Shared primitive update — `supervisor/scripts/lib/reflect.sh`

The skip path (lines 69-72) writes a one-line file and exits without tracking skip count or emitting an escalation event. This violates S3-P2 (escalation gate on consecutive skips).

Two project reflections independently identify that the reflection short-circuit path does not emit an `escalated` event after consecutive skips:

- **context-repository** (O2): "The reflection short-circuit rule has fired 18 consecutive times (June 1–June 9). S3-P2 requires an `escalated` event after N consecutive same-reason skips. The skip branch in the reflection job does not emit this event. Result: the governance system appears to be running while a project is abandoned."
- **command** (O1): "6-cycle skip threshold breached. Per S3-P2 / workspace CLAUDE.md, the synthesis job should have filed an URGENT at cycle 3. No URGENT exists for this pattern."

Add consecutive-skip tracking and escalation event emission:

```bash
# After line 70, before exit:
SKIP_COUNTER_FILE="$META_DIR/.${PROJECT}-skip-count"
PREV_COUNT=0
[[ -f "$SKIP_COUNTER_FILE" ]] && PREV_COUNT=$(cat "$SKIP_COUNTER_FILE" 2>/dev/null || echo 0)
NEW_COUNT=$((PREV_COUNT + 1))
echo "$NEW_COUNT" > "$SKIP_COUNTER_FILE"

if [[ "$NEW_COUNT" -ge 6 ]]; then
  # Emit escalated event per S3-P2
  printf '{"project":"%s","source":"reflect","eventType":"escalated","level":"warn","sourceType":"system","timestamp":%s,"details":{"consecutive_skips":%d}}\n' \
    "$PROJECT" "$(date +%s%3N)" "$NEW_COUNT" \
    >> "$WORKSPACE_TELEMETRY_DIR/events.jsonl"
fi
```

Reset the counter when a non-skip reflection runs (add `echo 0 > "$SKIP_COUNTER_FILE"` after the claude invocation succeeds).

**Blast radius:** All 8 projects (automatic). Closes the S3-P2 compliance gap for dormant projects. Does not change skip behavior — only adds observability.

**Impact:** Context-repository has been effectively abandoned for 30 days with no automated signal reaching the executive. Command has been quiet for 29 days with 6 skips and no escalation. The governance stack cannot distinguish "project is intentionally paused" from "project fell off the radar."

## Verification before action (required)

- Run `git log --oneline -10` on `/opt/workspace/supervisor`. Check if this change has already landed.
- Read `/opt/workspace/supervisor/scripts/lib/reflect.sh` lines 69-75. Check if skip-count tracking and escalation event emission are already present.
- If either is true, write a completion report stating "already landed" rather than re-applying.

## Acceptance criteria

- Skip-counter file creation and increment logic implemented after line 70
- Counter threshold (6 cycles) implemented
- Escalated event emitted to `events.jsonl` with correct schema (project, source, eventType, level, sourceType, timestamp, details.consecutive_skips)
- Counter reset logic implemented after successful (non-skip) reflection runs
- Change committed with clear message explaining the synthesis source and S3-P2 compliance
- Next dormant project reaching 6 consecutive skips emits escalated event (verifiable in next synthesis)
- Completion report at `runtime/.handoff/general-supervisor-synthesis-p-skip-escalation-complete-<iso>.md` pointing back to this handoff

## Escalation

URGENT if:
- Primary verification reveals the change is already landed. Write completion report "already landed" and close.
- The new skip-escalation code breaks the reflect.sh syntax or causes errors. Include full error output.
- Counter is not reset properly, causing false escalations on projects that then become active. Investigate and fix reset path.
