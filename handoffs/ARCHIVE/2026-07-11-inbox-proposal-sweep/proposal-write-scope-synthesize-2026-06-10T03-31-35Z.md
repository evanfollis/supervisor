---
from: synthesis-translator
to: general
date: 2026-06-10T03:31:35Z
priority: high
task_id: synthesis-p-write-scope-synthesize
source_synthesis: /opt/workspace/runtime/.meta/cross-cutting-2026-06-10T03-23-06Z.md
source_proposal: "Proposal 4: P-write-scope — Add `Write` to disallowedTools in synthesize.sh (CARRY-FORWARD, 4th cycle)"
---

# P-write-scope — Add `Write` to disallowedTools in synthesize.sh (CARRY-FORWARD, 4th cycle)

**Type:** Shared primitive update — `supervisor/scripts/lib/synthesize.sh`

The `be5ec96` patch added `Write` to reflect.sh's disallowedTools (line 112) but did NOT add it to synthesize.sh (line 56 lists only `"Edit" "NotebookEdit"`). The double-write defect that corrupted C84/C85 is still live in the synthesis job.

However, blocking `Write` also blocks the synthesis session from writing its own output file. The correct fix is post-hoc validation (C88's proposal): after the claude invocation returns, verify that no prior synthesis files were modified by the session.

Implement checksummed validation:

```bash
# Before the claude invocation, capture checksums:
declare -A PRIOR_SUMS
for prior in "$META_DIR"/cross-cutting-*.md; do
  PRIOR_SUMS["$prior"]=$(md5sum "$prior" | cut -d' ' -f1)
done

# After claude returns, verify no prior file was modified:
for prior in "$META_DIR"/cross-cutting-*.md; do
  [[ "$prior" == "$OUTPUT_FILE" ]] && continue
  current_sum=$(md5sum "$prior" | cut -d' ' -f1)
  if [[ "${PRIOR_SUMS[$prior]:-}" != "$current_sum" ]]; then
    echo "synthesize: ERROR — prior file corrupted: $prior" >&2
    git -C "$META_DIR" checkout -- "$prior" 2>/dev/null || true
  fi
done
```

**Blast radius:** Synthesis job only (automatic). Prevents historical synthesis corruption without breaking the output path. No impact on other projects or systems.

**Impact:** Protects against accidental Write-based corruption of prior synthesis files while preserving the synthesis job's ability to write its own output. This is safer than blocking `Write` entirely, since it allows the output file to be created while guaranteeing prior files cannot be touched.

## Verification before action (required)

- Run `git log --oneline -10` on `/opt/workspace/supervisor`. Check if this post-hoc validation change has already landed in synthesize.sh.
- Read `/opt/workspace/supervisor/scripts/lib/synthesize.sh` around the claude invocation (search for where claude is called). Check if checksum validation logic is present.
- If either is true, write a completion report stating "already landed" rather than re-applying.

## Acceptance criteria

- Before-invocation checksum capture implemented (builds associative array of prior synthesis files and their md5sums)
- After-invocation checksum verification implemented (loops through prior files and checks sums match)
- Corruption detection emits error message to stderr with corrupted filename
- Corrupted prior files are restored via `git checkout --` after corruption is detected
- Change committed with clear message explaining the synthesis source and the protection against double-write defects
- Synthesis job continues to write its own output file correctly (OUTPUT_FILE is excluded from prior-file list)
- Completion report at `runtime/.handoff/general-supervisor-synthesis-p-write-scope-synthesize-complete-<iso>.md` pointing back to this handoff

## Escalation

URGENT if:
- Primary verification reveals the change is already landed. Write completion report "already landed" and close.
- The checksum validation causes the synthesis job to fail on next run. Debug with full error output and determine if prior synthesis files are being accidentally corrupted.
- After this change, prior synthesis files cannot be recovered if legitimately corrupted by another process. Verify the `git checkout` restoration is working and that the error messaging is clear.
