---
from: synthesis-translator
to: general
date: 2026-06-06T15:29:27Z
priority: high
task_id: synthesis-self-sustaining-fix
source_synthesis: /opt/workspace/runtime/.meta/cross-cutting-2026-06-06T15-24-15Z.md
source_proposal: "Proposal 3: P-self-sustaining-fix — Exclude automation-generated activity from reflect.sh inactivity check (NEW)"
---

# P-self-sustaining-fix — Exclude self-generated telemetry from reflect.sh dormancy check

## Summary

The `reflect.sh` script includes a dormancy circuit breaker (lines 51-72) that skips reflection sessions for projects with no recent activity. This saves sessions during idle periods. However, for the supervisor project, the inactivity check **never fires** because the reflection loop's own outputs (session JSONL files, telemetry events) satisfy the activity heuristic. The prior reflection's JSONL is "recent," the prior telemetry events mention the project, and so the dormancy check always concludes there is activity.

**Result:** Supervisor reflections generate structurally identical output every 12h (18 sessions/cycle × 2 cycles/day = ~36 sessions/day) with zero marginal diagnostic value. These are self-sustaining automation artifacts.

**Pattern:** Telemetry events marked with `"source":"session-end-auto-summary"` and `"source":"reflect"` are self-generated. Session JSONL files matching `*reflect*` are reflection artifacts. These should not trigger activity detection.

## Proposal details

Exclude automation-generated activity from the inactivity check so that dormant projects (including supervisor during idle periods) short-circuit and conserve sessions.

## Change

**File:** `supervisor/scripts/lib/reflect.sh`

**Two locations:**

### 1. Lines ~60 (telemetry activity check)

Filter out self-generated telemetry:

```bash
# Before (line 60 approx):
TELEMETRY_COUNT=$(tail -n 5000 "$WORKSPACE_TELEMETRY_DIR/events.jsonl" 2>/dev/null | grep -F "\"$PROJECT\"" | wc -l || true)

# After:
TELEMETRY_COUNT=$(tail -n 5000 "$WORKSPACE_TELEMETRY_DIR/events.jsonl" 2>/dev/null \
  | grep -F "\"$PROJECT\"" \
  | grep -v '"source":"session-end-auto-summary"' \
  | grep -v '"source":"reflect"' \
  | wc -l || true)
```

### 2. Lines ~64-67 (JSONL file activity check)

Exclude reflection-session JSONL from the search:

```bash
# Before (lines 64-67 approx):
JSONL_RECENT=$(find "$SESSION_DIR" -maxdepth 1 -name '*.jsonl' -newermt "12 hours ago" 2>/dev/null | wc -l)

# After:
JSONL_RECENT=$(find "$SESSION_DIR" -maxdepth 1 -name '*.jsonl' \
  -not -name '*reflect*' -newermt "12 hours ago" 2>/dev/null | wc -l)
```

## Verification before action (required)

Run these before proceeding:

```bash
cd /opt/workspace
git log --oneline -5 supervisor/scripts/lib/reflect.sh
```

Check: Is there a recent commit that already adds these filters to the activity check? If yes, this proposal is already landed.

```bash
sed -n '60,70p' supervisor/scripts/lib/reflect.sh
```

Check: What does the current activity heuristic look like? Are there already filters on telemetry or JSONL?

## Acceptance criteria

- `supervisor/scripts/lib/reflect.sh` lines ~60 (telemetry check) exclude `session-end-auto-summary` and `reflect` sources
- Lines ~64-67 (JSONL check) exclude files matching `*reflect*` from the recency search
- Change committed with message: "Exclude self-generated activity from reflect.sh dormancy check — prevents supervisor self-sustaining reflection loop during idle periods"
- Adversarial review via `supervisor/scripts/lib/adversarial-review.sh` (structured change to shared primitive)
- Completion report: `/opt/workspace/runtime/.handoff/general-supervisor-synthesis-self-sustaining-fix-complete-<iso>.md`

## Expected impact

Combined with the prior two proposals (write-block, reflect-hook-allowlist), this change would:
- Eliminate false-positive URGENT URGENTs from hook writes (second proposal)
- Reduce wasted sessions from ~36/day to ~4/day during dormancy (this proposal)
- Tighten the reflection tool boundary (first proposal)

During active projects: no change (activity detection still works as intended).
During idle periods: supervisor reflections short-circuit instead of producing 18 identical sessions/cycle.

## Escalation

URGENT if:
- Commit history shows this change already landed within the past 3 cycles
- The telemetry event schema does not include a `source` field (verify with recent events.jsonl sample)

## Notes

This is one of three related reflect.sh improvements proposed in synthesis cycle 82 (see also: proposal-write-block and proposal-reflect-hook-allowlist). All three target the same file and could be landed together in a single attended session (~5 min total).

**Subsumption note (from synthesis):** This proposal completes the intent of earlier carry-forward P5 (Idle-period cadence reduction, open 15 cycles) which was blocked by the self-sustaining activity loop. P5 is now subsumed by this proposal.
