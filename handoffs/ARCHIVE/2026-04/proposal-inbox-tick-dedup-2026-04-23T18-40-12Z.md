---
from: synthesis-translator
to: general
date: 2026-04-23T18-40-12Z
priority: high
task_id: synthesis-inbox-tick-dedup
source_synthesis: /opt/workspace/runtime/.meta/cross-cutting-2026-04-23T15-24-05Z.md
source_proposal: Proposal 3 — INBOX tick-skip deduplication (3rd cycle)
---

# INBOX tick-skip deduplication (3rd cycle)

## Problem

When the supervisor tick skips due to a dirty tree, it escalates by writing a new URGENT file to INBOX. Each skip cycle creates a new file for the same root cause. Currently INBOX holds 31 items, 29 of which are tick-skip URGENTs for the identical root cause (dirty-tree guard blocking untracked file).

**Signal degradation:** INBOX signal-to-noise ratio is now 6.5% (2 of 31 items are substantive). Deduplication would prevent this noise pile from recurring once Proposal 1 (tick dirty-tree fix) lands.

## Proposed Fix

**File**: `supervisor/scripts/lib/supervisor-tick.sh`, S3-P2 escalation section

When an URGENT for the same root cause already exists in INBOX, subsequent escalations update that file's metadata rather than creating new files.

**Sketch:**
```bash
existing=$(ls "$INBOX"/URGENT-tick-escalation-*.md 2>/dev/null | head -1)
if [[ -n "$existing" ]]; then
  sed -i "s/^Skip count:.*/Skip count: $skip_count (updated $(date -u +%FT%TZ))/" "$existing"
else
  write_tick_escalation "$INBOX" "$skip_count" "$skip_reason"
fi
```

This updates the existing escalation file's metadata rather than creating a new file (which would add to the noise).

**Blast radius:** Supervisor tick INBOX writes only. Automatic. Prevents the 29-item noise pile from recurring. Does not suppress the first escalation.

## Rationale

This is the 3rd cycle recommending this change. It is now at the deduplication threshold. The sketch provided is a starting point — the actual implementation may need to:
- Account for different root causes (not all tick skips are dirty-tree related)
- Preserve a timestamp trail in the escalation file
- Coordinate with the saturation exception (Proposal 4)

## Verification before action (required)

- Read `supervisor/scripts/lib/supervisor-tick.sh`. Locate the S3-P2 escalation section (near the end of the file). Check if deduplication logic already exists.
- Check INBOX contents: `ls /opt/workspace/supervisor/handoffs/INBOX/URGENT-tick-escalation-*.md`. Count how many such files exist. If >5, deduplication is needed.
- If deduplication logic is already present, write a completion report stating "already implemented" rather than re-applying.

## Acceptance criteria

- When `supervisor-tick.sh` needs to escalate a tick skip, it checks if a `URGENT-tick-escalation-*.md` file already exists in INBOX.
- If one exists, the existing file is updated (Skip count, timestamp) rather than a new file being created.
- If none exists, the first escalation file is written as before.
- Change is committed with a message explaining deduplication for repeated root causes.
- Completion report confirms the logic is in place, the test case (existing URGENT being updated on the next skip), and the commit SHA.

## Escalation

URGENT if:
- Verification shows the logic is already implemented (skip with "already implemented" note).
- The implementation handles different root causes but the current 29-file pile is from identical root causes. Clarify that only identical-root-cause dedup is needed for immediate relief.
- The implementation conflicts with Proposal 4 (saturation exception). Coordinate via comments in both completion reports.
