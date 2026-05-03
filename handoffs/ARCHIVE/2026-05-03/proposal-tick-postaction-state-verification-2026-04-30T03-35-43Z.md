---
from: synthesis-translator
to: general
date: 2026-04-30T03:35:43Z
priority: medium
task_id: synthesis-tick-postaction-verification
source_synthesis: /opt/workspace/runtime/.meta/cross-cutting-2026-04-30T03-26-25Z.md
source_proposal: Proposal 3 — Post-action state verification in tick wrapper
---

# Tick wrapper: post-action state verification and consecutive-failure tracking

## Problem

Two supervisor infrastructure gaps are causing silent failures:

1. **Ghost-write detection:** Ticks claim to have created or materialized files in their logs, but the files don't exist on disk. The tick wrapper merges the branch without verifying the claimed state. This produces "ghost" FR files (friction directory ends at FR-0037 while ticks claim FR-0038/0039 written) and prevents accurate tick telemetry.

2. **Consecutive-failure tracking:** When a tick invocation fails, the wrapper does not track consecutive failures. The S3-P2 escalation gate requires 2+ consecutive failures to emit an `escalated` event, but there is no state file tracking failure count. This has allowed invocation failures to recur for 3+ cycles without escalation.

## Solution

Add two verification blocks to the tick wrapper (likely `supervisor/scripts/lib/supervisor-tick.sh` or equivalent) after the merge-to-main step and at the end of the invocation.

**Block 1: Ghost-write detection (after merge)**

```bash
# After tick branch merge to main, before emitting session_reflected:
for claimed_file in $(grep -oP '(?:materialized|created)\s+\K\S+' "$tick_log"); do
  [ -f "$claimed_file" ] || emit_escalated "ghost-write: $claimed_file claimed but absent"
done
```

**Block 2: Consecutive-failure tracking (in wrapper exit)**

```bash
# Consecutive-failure tracking (call before wrapper exit):
FAIL_COUNT_FILE="$RUNTIME/.meta/tick-consecutive-failures"
count=$(cat "$FAIL_COUNT_FILE" 2>/dev/null || echo 0)
if [ "$exit_code" -ne 0 ]; then
  echo $((count + 1)) > "$FAIL_COUNT_FILE"
  [ $((count + 1)) -ge 2 ] && emit_escalated "tick-invocation-failure" "consecutive=$((count+1))"
else
  echo 0 > "$FAIL_COUNT_FILE"
fi
```

## Blast radius

- Supervisor project only (tick wrapper automation)
- Low risk — adds defensive checks, no behavior change to success path
- Automatic — runs on every tick invocation
- Does not affect project repos

## Verification before action (required)

- Check if ghost-write detection already exists in the tick wrapper — search for "ghost" or "claimed_file"
- Check if consecutive-failure tracking already exists — search for "FAIL_COUNT_FILE" or "consecutive"
- If both are present and functional, write a completion report stating they are already implemented rather than re-applying
- If implemented but not working (ghost-state and consecutive failures still occurring), debug the implementation before this handoff is marked complete — may indicate the code is present but disabled or the `emit_escalated` function is non-functional

## Acceptance criteria

- Ghost-write detection block is added to the tick wrapper after merge-to-main, before session_reflected emission
- Consecutive-failure tracking block is added to the wrapper exit handler
- The blocks correctly parse the tick log, check file existence, and invoke `emit_escalated` for violations
- Change committed with clear message (e.g., "supervisor-tick: add ghost-write detection and consecutive-failure tracking")
- On the next tick cycle, verify:
  - Ghost FRs are detected and escalated (currently `friction/` ends at FR-0037, ticks claim FR-0038/0039)
  - A second consecutive invocation failure produces an escalated event
- Completion report at `/opt/workspace/supervisor/handoffs/INBOX/general-tick-postaction-verification-complete-<iso>.md`

## Critical note

This proposal has recurred for 1+ cycles with 2 copies in INBOX. The code sketch is unchanged from prior recommendations. Ghost-state remains unresolved (synthesis confirms: "Ghost FRs: `ls friction/` ends at FR-0037. Ticks continue claiming FR-0038/0039 written. 13+ windows."). This fix is load-bearing — the supervisor's state integrity depends on it.
