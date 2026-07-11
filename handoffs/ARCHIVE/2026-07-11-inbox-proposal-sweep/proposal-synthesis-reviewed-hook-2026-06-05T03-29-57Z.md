---
from: synthesis-translator
to: general
date: 2026-06-05T03:29:57Z
priority: medium
task_id: synthesis-reviewed-event-hook
source_synthesis: /opt/workspace/runtime/.meta/cross-cutting-2026-06-05T03-26-55Z.md
source_proposal: P-synthesis-reviewed-hook (NEW from cycle 19)
---

# P-synthesis-reviewed-hook — Wire `synthesis_reviewed` event to executive session

## Proposal body (from synthesis)

**Type:** Enforcement gate — hook change.

**Sketch:** Add to workspace `SessionEnd` hook or executive session prompt: emit `synthesis_reviewed` event when the session read a synthesis file. Currently a 19-cycle gap.

**Blast radius:** General session only (automatic). Closes the event-emission gap that makes it impossible to determine from telemetry whether any synthesis was acted on.

## Context

The synthesis loop has been running at full cadence for 19 cycles, but there is a gap: the executive session (general) does not emit a `synthesis_reviewed` event when it reads and processes synthesis files. This makes it impossible to distinguish between:
- A synthesis that was read and acted on (should emit `synthesis_reviewed`)
- A synthesis that was read but ignored (should emit `synthesis_reviewed` with a note)
- A synthesis that was never read by the executive (no event emitted)

Currently, the gap is 19 cycles (no `synthesis_reviewed` events since synthesis began reporting them as expected).

## Verification before action (required)

- Search `supervisor/scripts/lib/*.sh` and `/root/.claude/hooks/*` for any existing `synthesis_reviewed` event emission. If found, verify it is working and check recent telemetry.
- Check `events/supervisor-events.jsonl` for any `synthesis_reviewed` entries in the last 7 days: `grep -c synthesis_reviewed events/supervisor-events.jsonl`.
- If the event is already being emitted, write a completion report stating "event already present; gap is (N) entries in last 7 days" and close.

## Acceptance criteria

- One of the following options:
  
  **Option A (recommended):** Add to `session-end-auto-summary.sh` or similar executive-scoped hook:
  ```bash
  if [[ -d /opt/workspace/runtime/.meta ]]; then
    latest_synthesis=$(ls -1t /opt/workspace/runtime/.meta/cross-cutting-*.md 2>/dev/null | head -1)
    if [[ -n "$latest_synthesis" ]]; then
      # Session has access to synthesis files; emit the event
      emit_event "synthesis_reviewed" "Session ended after reading workspace synthesis."
    fi
  fi
  ```
  
  **Option B:** Add to `/opt/workspace/supervisor/CLAUDE.md` executive prompt, instruction to emit the event when synthesis files are read.

- Event shape must match the standard: `{"ts":"<iso>","agent":"<agent>","type":"synthesis_reviewed","ref":"<synthesis-file-path>","note":"<one-line>"}`.
- Change committed with clear message: "Emit synthesis_reviewed event to close telemetry gap on synthesis consumption."
- Adversarial review optional (telemetry emission, no logic change).
- Completion report at `runtime/.handoff/general-synthesis-reviewed-complete-<iso>.md` pointing to the change and this handoff.

## Escalation

URGENT if:
- Session-end hooks are not working or the `emit_event` function is unavailable in that context (check `session-end-auto-summary.sh` for the pattern).
- The proposal is based on a misunderstanding of which session should emit the event (clarify with Evan if uncertain).

---

**Note:** This is a new finding from cycle 19. It pairs with P-synthesis-verify as a meta-observability improvement. Together, they address the two genuinely new patterns from the latest synthesis cycle.
