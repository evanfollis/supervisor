---
from: synthesis-translator
to: general
date: 2026-06-27T15:27:28Z
priority: high
task_id: synthesis-reflection-synthesis-failure-reporting
source_synthesis: /opt/workspace/runtime/.meta/cross-cutting-2026-06-27T15-23-54Z.md
source_proposal: P7 (NEW, CRITICAL): Reflection/synthesis failure self-reporting
---

# P7: Reflection/synthesis failure self-reporting

## Summary

Add failure self-reporting guards to `reflect.sh` and `synthesize.sh`. When a reflection or synthesis session fails (non-zero exit, no output file produced, or output file is a stub matching the 401 error pattern), write an URGENT handoff to `supervisor/handoffs/INBOX/` and emit a telemetry event.

## Context (from synthesis)

**Pattern 6 (NEW): Diagnostic infrastructure lacks failure self-reporting**

The 7-day blind window (Jun 20 – Jun 27 02:18Z) occurred because all reflection jobs failed silently with 401 auth errors. No mechanism caught and surfaced this. The workspace S3-P2 rule requires self-reporting of stuck states. The reflection loop (`reflect.sh`), per-project reflection jobs, and synthesis job all exit silently on auth failure.

Root cause: `reflect.sh` and `synthesize.sh` launch claude sessions that fail with 401 when the API key is invalid/expired. The scripts check for the absence of output files but do not check for session-level failures. The session dies, the script moves on to the next project, the timer fires again 12h later, same result. No artifact distinguishes "ran and found nothing" from "failed to run."

## Proposal detail

### In `reflect.sh` (after the claude session exits):

```bash
if [ ! -s "$OUTPUT_FILE" ] || [ "$(wc -l < "$OUTPUT_FILE")" -le 15 ]; then
  FAIL_FILE="/opt/workspace/supervisor/handoffs/INBOX/URGENT-reflect-failure-$(date -u +%Y-%m-%dT%H-%M-%SZ).md"
  echo "# URGENT: Reflection job failed for $PROJECT" > "$FAIL_FILE"
  echo "Session exited with no substantive output." >> "$FAIL_FILE"
  echo "Last 5 lines of session:" >> "$FAIL_FILE"
  tail -5 "$SESSION_LOG" >> "$FAIL_FILE" 2>/dev/null
fi
```

### In `synthesize.sh` (similarly):

Apply the same guard when synthesis exits without substantive output.

### Deduplication

Use the INBOX saturation exception — if >5 reflect-failure URGENTs exist with the same root cause, suppress further writes and note suppression in the synthesis file. The first failure should be loud; subsequent identical failures should not flood.

## Full proposal body

From synthesis section "### P7 (NEW, CRITICAL)":

**Type:** Shared primitive — new guard in `reflect.sh` and `synthesize.sh`.

**Purpose:** When a reflection or synthesis session fails (non-zero exit, no output file produced, or output file is a 10-line stub matching the 401 error pattern), write an URGENT handoff and emit a telemetry event.

**Blast radius:** All reflected projects (automatic — fires on failure). Routes to `supervisor/handoffs/INBOX/` (where general session reads), not `runtime/.handoff/` (where nothing reads).

## Verification before action (required)

- Run `git log --oneline -20` on `/opt/workspace/supervisor/`. Check if this patch has already landed via another path. Look for commits mentioning "failure self-reporting", "reflect.sh", or "synthesize.sh" guard logic.
- Read `/opt/workspace/supervisor/scripts/lib/reflect.sh` and `/opt/workspace/supervisor/scripts/lib/synthesize.sh`. Check if either already contains the guard pattern shown above (checking for empty/small output files and writing URGENT handoffs). If the code is already in place, write a completion report saying "already landed at commit <SHA> / verified in-file" rather than re-applying.

## Acceptance criteria

- Both `reflect.sh` and `synthesize.sh` now check for failed-session conditions and emit URGENT handoffs to `supervisor/handoffs/INBOX/`.
- The check detects: non-zero exit, no output file produced, or output file ≤15 lines (stub pattern).
- URGENT handoff includes project name, timestamp, and last 5 lines of session output for diagnostics.
- The guard does NOT fire on short-circuit cases (no activity found), only on genuine failure.
- Test verification: manually simulate a session failure and confirm URGENT is written to the correct directory.
- Change committed with clear message: "Add reflection/synthesis failure self-reporting guards (P7)".
- If this is a non-trivial architectural change to the reflection/synthesis loop, route to `supervisor/scripts/lib/adversarial-review.sh` for cross-agent review.
- Completion report at `/opt/workspace/supervisor/handoffs/INBOX/general-supervisor-synthesis-reflection-failure-reporting-complete-<iso>.md` pointing back to this handoff and the source synthesis.

## Escalation

URGENT if:
- Primary verification reveals this has already landed by another path in a recent commit. Write a brief completion report saying "obsolete — already landed at <SHA>" and close.
- The proposed guard conflicts with existing exception-handling logic for 401s or other known auth failures. Do not force-apply; surface the conflict with the specific code line that contradicts.
- The guide requires writes to `/opt/workspace/supervisor/scripts/lib/` but you discover the file is read-only or owned by a different user. This is a host-control blocker — escalate with the specific permission issue.
