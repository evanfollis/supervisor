---
from: synthesis-translator
to: general
date: 2026-05-31T15:27:59Z
priority: high
task_id: synthesis-p8-monotonic-skip-counter
source_synthesis: /opt/workspace/runtime/.meta/cross-cutting-2026-05-31T15-23-50Z.md
source_proposal: P8 — Monotonic skip counter for tick escalation
---

# P8 — Monotonic skip counter for tick escalation

**Type**: Shared primitive edit — `supervisor/scripts/lib/supervisor-tick.sh`

**Change**: Instead of overwriting the URGENT file with a new skip count, append to a counter file (or read the current count and increment). The URGENT file should reflect the true cumulative skip count.

**Current behavior** (lines 60-68):
```bash
first_seen=$(awk '/^First escalated: /{print $3; exit}' "$URGENT_FILE" 2>/dev/null || true)
first_seen="${first_seen:-$ISO_NOW}"
cat > "$URGENT_FILE" <<INBOX_EOF
# URGENT — supervisor tick escalated after ${consecutive} consecutive skips

Reason: ${reason}
First escalated: ${first_seen}
Latest skip: ${ISO_NOW}
Consecutive skips: ${consecutive}
```

The `consecutive` counter is rewritten each cycle instead of being incremented, and concurrent or near-concurrent writers can race on the file. This causes the counter to alternate between values (9 and 10 observed) instead of monotonically increasing.

**Blast radius**: Supervisor only. Automatic.

**Evidence of the problem**: The URGENT file currently shows skip counts of 9–10, but the actual skip count is ~72+, meaning the file understates severity by ~7×.

## Verification before action (required)

- Run `git log --oneline -5` on `supervisor/`. Check if a monotonic counter fix has already landed.
- Read `supervisor/scripts/lib/supervisor-tick.sh` lines 60-68. Verify the counter is still using the overwrite pattern and not yet incremented.
- If either check shows this is already applied, write a completion report stating "already landed" rather than re-applying.

## Acceptance criteria

- The skip counter now monotonically increases (does not alternate or reset).
- The counter accurately reflects the true cumulative skip count, not just the consecutive skips in the current window.
- Proposed implementation: use a separate counter file (e.g., `supervisor/handoffs/INBOX/.escalation-counter-<reason-hash>`) that is incremented rather than overwritten, or read the prior count from the URGENT file and increment it.
- Change committed with clear message explaining the synthesis source and the fix for the race condition.
- Completion report at `runtime/.handoff/general-supervisor-synthesis-p8-complete-<iso>.md` pointing back to this handoff.

## Escalation

URGENT if:
- Primary verification reveals this fix has already landed. Write a brief completion report saying "already landed" and close.
- The fix requires deeper changes to the escalation file structure (e.g., moving to a counter-per-reason-hash file). Escalate with the specific technical approach and proposed changes before implementing.
