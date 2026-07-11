---
from: synthesis-translator
to: general
date: 2026-06-09T15:31:16Z
priority: high
task_id: synthesis-synthesize-write-scope
source_synthesis: /opt/workspace/runtime/.meta/cross-cutting-2026-06-09T15-27-48Z.md
source_proposal: P-write-scope — Add `Write` to disallowedTools in synthesize.sh
---

# P-write-scope — Add `Write` to disallowedTools in synthesize.sh

## Problem

The synthesis prompt already instructs the LLM to write to `$OUTPUT_FILE`. However, the LLM session currently has unrestricted `Write` access to historical artifacts via the symlink target (LATEST_SYNTHESIS). This has caused systematic overwrites:

- `cross-cutting-2026-06-07T15-24-57Z.md` (C84 slot) was overwritten by C85 output
- `cross-cutting-2026-06-08T03-25-09Z.md` was overwritten by C85 output
- C83 and C84 original content is permanently lost

**Root cause:** The `--disallowedTools` list blocks `Edit` but not `Write`. The LLM reads `LATEST_SYNTHESIS` during research, then writes to both the intended output file and the symlink target.

Append-only semantics for synthesis files are required but not enforced.

## Solution

Apply post-hoc validation after the synthesis claude call completes. In `supervisor/scripts/lib/synthesize.sh`, after line 57 (after claude -p returns):

```bash
# Verify no prior synthesis files were modified during this run
RUN_START=$(stat -c %Y "$OUTPUT_FILE" 2>/dev/null || echo 0)
for prior in "$META_DIR"/cross-cutting-*.md; do
  [[ "$prior" == "$OUTPUT_FILE" ]] && continue
  if [[ $(stat -c %Y "$prior") -gt "$RUN_START" ]]; then
    echo "synthesize: ERROR — prior synthesis file modified during run: $prior" >&2
    git checkout -- "$prior" 2>/dev/null || true
  fi
done
```

This captures the mtime of the newly-created output file and checks that no prior synthesis files have a newer timestamp. If any were modified (by the LLM writing through the symlink), restores them from git.

**Alternative approach:** Capture md5sums of all existing `cross-cutting-*.md` files before the claude call, verify after, and restore any that changed.

## Verification before action (required)

- Read `supervisor/scripts/lib/synthesize.sh` and verify the `--disallowedTools` line (around line 56) does NOT include `Write`
- Verify the output file path is created/refreshed correctly on the last successful synthesis run
- Check git log to confirm no synthesis overwrites have already been fixed via another path

## Acceptance criteria

- Post-hoc validation is inserted after the claude call in synthesize.sh
- No prior `cross-cutting-*.md` files can be modified by a synthesis run (test by running a synthesis and confirming prior files remain unchanged)
- Change committed with message explaining the write-access constraint fix
- Completion report notes the verification: "Confirmed synthesis run did not overwrite prior files"

## Blast radius

Synthesis job only (automatic). Does not affect project sessions.

## Escalation

URGENT if:
- The validation logic is discovered to be already in place from a prior fix — report "already landed at commit <SHA>" and close without re-applying
- The check discovers that the current synthesis file itself was just written before this run (false positive; may indicate the claude run is not completing normally)
