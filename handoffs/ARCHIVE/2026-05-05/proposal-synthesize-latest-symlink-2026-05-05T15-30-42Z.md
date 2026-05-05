---
from: synthesis-translator
to: general
date: 2026-05-05T15:30:42Z
priority: critical
task_id: synthesis-fix-latest-symlink
source_synthesis: /opt/workspace/runtime/.meta/cross-cutting-2026-05-05T15-25-53Z.md
source_proposal: Proposal 2 — Fix synthesize.sh:89 LATEST_SYNTHESIS corruption
---

# Proposal 2 [CRITICAL, REPEAT — cycle 12]: Fix synthesize.sh:89 LATEST_SYNTHESIS corruption

Same fix, confirmed with primary evidence this window. The synthesis delivery mechanism has been broken for 3+ cycles — the synthesize.sh script was overwriting the target synthesis file with a path string instead of updating the symlink.

**Exact change** (`/opt/workspace/supervisor/scripts/lib/synthesize.sh:89`):

```diff
-echo "$OUTPUT_FILE" > "$WORKSPACE_LATEST_SYNTHESIS_PTR"
+ln -sfn "$(basename "$OUTPUT_FILE")" "$WORKSPACE_LATEST_SYNTHESIS_PTR"
```

**Current behavior (broken):** The script follows the LATEST_SYNTHESIS symlink and overwrites the target synthesis file with a path string (67 bytes), making synthesis output unreadable.

**Fixed behavior:** The script updates the symlink itself to point to the new synthesis file. This preserves the actual synthesis markdown content.

**Blast radius:** Synthesis pipeline only. Automatic. Fixes every future synthesis delivery.

## Verification before action (required)

- Run `cat /opt/workspace/supervisor/scripts/lib/synthesize.sh | sed -n '88,90p'` to verify line 89 still contains the broken code.
- Run `git log --oneline -20 /opt/workspace/supervisor/scripts/lib/synthesize.sh` to confirm this fix hasn't already been applied.
- Read the current `/opt/workspace/runtime/.meta/LATEST_SYNTHESIS` pointer. It should be a symlink, not a file containing a path string. If it's a file with a path string, that confirms the current bug.

## Acceptance criteria

- Line 89 of synthesize.sh is changed from `echo` to `ln -sfn`.
- Change committed with clear message: "Fix LATEST_SYNTHESIS pointer — use symlink update not file overwrite (synthesis proposal 2)"
- Post-fix verification: run the synthesis script and verify that LATEST_SYNTHESIS is a valid symlink pointing to the most recent synthesis markdown file, not a file containing a path string.

## Escalation

URGENT if:

- Primary verification reveals this fix has already landed via another path. Write a completion report stating "already landed" with the commit SHA.
- The fix causes synthesis script to fail (unusual — it should be transparent). Check for any dependent code that reads or follows LATEST_SYNTHESIS.
