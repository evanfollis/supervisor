---
from: synthesis-translator
to: general
date: 2026-06-07T15:27:15Z
priority: high
task_id: synthesis-exclude-automation-activity
source_synthesis: /opt/workspace/runtime/.meta/cross-cutting-2026-06-07T15-24-57Z.md
source_proposal: "P-self-sustaining-fix — Exclude automation-generated activity from reflect.sh inactivity check (CARRY-FORWARD, 3rd cycle)"
---

# P-self-sustaining-fix — Exclude automation-generated activity from reflect.sh inactivity check

**Type:** Shared primitive update — `supervisor/scripts/lib/reflect.sh`

**Context:** The reflection → synthesis → INBOX pipeline has produced accurate diagnosis for 24 consecutive cycles with zero execution conversion. The self-sustaining mechanism is unchanged: reflect.sh's inactivity check (lines 60–70) counts session-end-hook telemetry events and JSONL files as "activity," so the observation system's own artifacts prevent the short-circuit from firing. The automated stack continues to generate ~36 Claude Sonnet sessions/day across 8 projects during dormancy.

**Sketch:**

Replace line 60:
```bash
TELEMETRY_COUNT=$(tail -n 5000 "$WORKSPACE_TELEMETRY_DIR/events.jsonl" 2>/dev/null \
  | grep -F "\"$PROJECT\"" \
  | grep -v '"source":"session-end-auto-summary"' \
  | grep -v '"source":"reflect"' \
  | wc -l || true)
```

Replace line 66:
```bash
JSONL_RECENT=$(find "$SESSION_DIR" -maxdepth 1 -name '*.jsonl' \
  -not -name '*reflect*' -newermt "12 hours ago" 2>/dev/null | wc -l)
```

**Blast radius:** All 8 projects (automatic). Reduces dormancy sessions from ~36/day to ~4/day. Independent of P1.

## Verification before action (required)

- Run `git log --oneline -20 supervisor/scripts/lib/reflect.sh`. Check if this proposal has already landed via another path.
- Read `supervisor/scripts/lib/reflect.sh` lines 60 and 66. Check if the specified filtering is already present.
- If either is true, write a completion report stating "already landed at commit <SHA> / verified in-file" rather than re-applying.

## Acceptance criteria

- Line 60 applies both grep filters for `session-end-auto-summary` and `reflect` sources.
- Line 66 excludes `*reflect*` JSONL files from the find.
- Change committed with clear message explaining the synthesis source.
- Adversarial review via `supervisor/scripts/lib/adversarial-review.sh` before committing (non-trivial shared primitive affecting all projects).
- Completion report at `/opt/workspace/supervisor/handoffs/ARCHIVE/YYYY-MM/general-synthesis-exclude-automation-activity-complete-<iso>.md` pointing back to this handoff and the source synthesis.

## Escalation

URGENT if:
- Primary verification reveals the proposal is based on stale state (the fix has already landed by another path). Write a brief completion report saying "obsolete — already landed" and close.
- The proposal conflicts with a more recent decision. Do not force-apply; escalate with the conflict named.
