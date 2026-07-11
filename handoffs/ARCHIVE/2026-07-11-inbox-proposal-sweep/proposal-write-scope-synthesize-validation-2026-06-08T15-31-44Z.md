---
from: synthesis-translator
to: general
date: 2026-06-08T15:31:44Z
priority: high
task_id: synthesis-write-scope-synthesize-validation
source_synthesis: /opt/workspace/runtime/.meta/cross-cutting-2026-06-08T15-27-05Z.md
source_proposal: Proposal 1 — P-write-scope — Add Write constraints to synthesis job (NEW)
---

# P-write-scope — Add Write constraints to synthesis job

## Summary

The double-write defect identified in prior cycles is confirmed to be **systematic**: each synthesis run since C83 has been overwriting the prior cycle's output file with its own content, destroying historical records. C83 and C84 artifacts are permanently lost.

**Root cause (likely):** The `claude -p` session reads `LATEST_SYNTHESIS` (a symlink to the prior cycle's file) during its research phase. When it writes output, it may be writing to both the intended `$OUTPUT_FILE` path AND the symlink target it previously read, or the LLM may be resolving the symlink and treating the resolved path as an output location. `Edit` is blocked but `Write` is not.

## Proposed patch

Add post-hoc validation to `supervisor/scripts/lib/synthesize.sh` after the claude command returns. This checks that no prior synthesis files were modified:

```bash
# After claude -p returns, verify no prior synthesis files were modified:
for prior in "$META_DIR"/cross-cutting-*.md; do
  [[ "$prior" == "$OUTPUT_FILE" ]] && continue
  if [[ "$prior" -nt "$RUN_START" ]]; then
    echo "synthesize: ERROR — prior synthesis file modified: $prior" >&2
    # Restore from git or backup
  fi
done
```

Insert this validation block after line 57 (after the claude command completes) and before the OUTPUT_FILE existence check at line 59. Capture `RUN_START` at the top of the script (near line 16) as: `RUN_START=$(date +%s)`.

## Blast radius

Synthesis job only (automatic). Does not affect project sessions. No credentials required.

## Verification before action (required)

- Run `git -C /opt/workspace/supervisor log --oneline -10` to verify the patch hasn't landed via another path.
- Read `/opt/workspace/supervisor/scripts/lib/synthesize.sh` lines 48-62. Check if post-hoc validation loop exists.
- If either shows the patch is already applied, write a completion report stating "already landed" rather than re-applying.

## Acceptance criteria

- The post-hoc validation loop is added to `synthesize.sh` after the claude command.
- `RUN_START` is captured at the script start.
- Change committed with a message explaining the systematic double-write defect fix.
- Adversarial review via `supervisor/scripts/lib/adversarial-review.sh` (non-trivial change to critical infra).
- Completion report at `/opt/workspace/supervisor/handoffs/INBOX/general-synthesis-validation-complete-<iso>.md` pointing back to this handoff and the source synthesis.

## Escalation

URGENT if:
- The validation logic itself prevents legitimate synthesis writes (test before shipping).
- Primary verification reveals the patch is based on stale defect state (another fix landed, double-write already fixed).
