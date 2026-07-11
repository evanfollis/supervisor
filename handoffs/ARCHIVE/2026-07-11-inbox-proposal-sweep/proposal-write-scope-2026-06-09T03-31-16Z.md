---
from: synthesis-translator
to: general
date: 2026-06-09T03:31:16Z
priority: high
task_id: synthesis-write-scope
source_synthesis: /opt/workspace/runtime/.meta/cross-cutting-2026-06-09T03-27-21Z.md
source_proposal: P-write-scope — Add post-hoc validation to synthesis job
---

# P-write-scope — Add post-hoc validation to synthesis job

**Type:** Shared primitive update — `supervisor/scripts/lib/synthesize.sh`

**Carry-forward count:** 2nd cycle

After the `claude -p` call returns (line 57), add post-hoc validation:

```bash
# Verify no prior synthesis files were silently overwritten by the LLM session:
for prior in "$META_DIR"/cross-cutting-*.md; do
  [[ "$prior" == "$OUTPUT_FILE" ]] && continue
  if [[ "$prior" -nt "$RUN_START_TS" ]]; then
    echo "synthesize: ERROR — prior file modified: $prior" >&2
    git checkout -- "$prior" 2>/dev/null || true
  fi
done
```

Also requires adding `RUN_START_TS=$(date -r /tmp/.synth-start-$$)` or equivalent timestamp capture before the `claude -p` invocation (around line 46, before the prompt construction).

**Blast radius:** Synthesis job only (automatic). Does not affect project sessions.

**Rationale:** The synthesis double-write defect is confirmed systematic and ongoing. Verified live with md5sum comparison: the `--disallowedTools` list blocks `Edit` but not `Write`. The LLM session reads `LATEST_SYNTHESIS` (a symlink to the prior cycle's file) during research, then writes to both the intended `$OUTPUT_FILE` and the symlink target, overwriting prior cycle output. Each synthesis run overwrites the prior cycle's file with its own content, causing permanent data loss. C83's original content was replaced by C84 content; C84's slot and C85's slot are byte-identical. This patch detects when prior synthesis files are modified and restores them.

## Verification before action (required)

- Run `git log --oneline -20` on `/opt/workspace/supervisor` and verify no recent commits touched `synthesize.sh` with "post-hoc validation" or "RUN_START_TS".
- Read `/opt/workspace/supervisor/scripts/lib/synthesize.sh` lines 46–57. Verify there is no `RUN_START_TS` capture and no `for prior in "$META_DIR"/cross-cutting-*.md` loop after the `claude -p` call.
- Check `ls -la /opt/workspace/runtime/.meta/cross-cutting-*.md | head -10` to confirm synthesis files exist and can be tested.
- If the validation code is already present, write a completion report stating "already landed at commit <SHA>" rather than re-applying.

## Acceptance criteria

- Add `RUN_START_TS=$(date -r /tmp/.synth-start-$$)` (or equivalent timestamp before `claude -p`) before line 46.
- Add the post-hoc validation loop after line 57 to detect and restore overwritten prior synthesis files.
- Change committed with clear message explaining the synthesis source and the double-write defect fix.
- Adversarial review via `supervisor/scripts/lib/adversarial-review.sh` — this is a critical data-integrity fix for the synthesis pipeline.
- Completion report at `/opt/workspace/supervisor/handoffs/INBOX/general-write-scope-complete-<iso>.md` pointing back to this handoff and the source synthesis.
- After applying, verify the logic works by:
  - Running synthesize.sh manually (or waiting for the next scheduled run)
  - Confirming the `synthesize: ERROR — prior file modified` message does NOT appear (normal case) or DOES appear (if a write overlap happens to occur during testing)
  - Checking that `cross-cutting-*.md` files exist and have the expected content

## Escalation

URGENT if:
- Primary verification reveals this patch has already landed by another path. Write a brief completion report and close.
- The timestamp capture method (`date -r /tmp/.synth-start-$$`) conflicts with the actual shell environment or the file system. Replace with an appropriate timestamp method for the target environment.
- The restoration logic (`git checkout -- "$prior"`) fails because the synthesis job doesn't have git write access. Escalate with evidence and ask for an alternative recovery method.
