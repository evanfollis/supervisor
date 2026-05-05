---
from: synthesis-translator
to: supervisor
date: 2026-05-05T03:26:47Z
priority: critical
task_id: synthesis-latest-synthesis-pointer
source_synthesis: /opt/workspace/runtime/.meta/cross-cutting-2026-05-05T03-23-14Z.md
source_proposal: "Proposal 3 [CRITICAL, REPEAT — cycle 2]: Fix LATEST_SYNTHESIS pointer mechanism"
---

# Fix LATEST_SYNTHESIS pointer mechanism

**Exact change** (`/opt/workspace/supervisor/scripts/lib/synthesize.sh`):

Replace the symlink-through write with an atomic plain-file pointer:
```bash
rm -f "$META_DIR/LATEST_SYNTHESIS"
printf '%s\n' "$(basename "$OUTPUT_FILE")" > "$META_DIR/LATEST_SYNTHESIS"
```

And update all readers to resolve: `cat LATEST_SYNTHESIS` gives a filename, then read that file.

**Blast radius:** Synthesis pipeline + any automation reading LATEST_SYNTHESIS. The current mechanism is already broken (reads return 67 bytes), so this is a repair, not a behavior change.

## Verification before action (required)

- Check current LATEST_SYNTHESIS behavior: `ls -la /opt/workspace/runtime/.meta/LATEST_SYNTHESIS; wc -c /opt/workspace/runtime/.meta/LATEST_SYNTHESIS`
- Expected broken state: symlink pointing to a 67-byte stub file
- Check if synthesize.sh has already been patched: `grep -A 2 "rm -f.*LATEST_SYNTHESIS" /opt/workspace/supervisor/scripts/lib/synthesize.sh | head -5`
- If the file is >500 bytes and contains markdown content, the fix is already landed

## Acceptance criteria

- Edit `/opt/workspace/supervisor/scripts/lib/synthesize.sh` to replace symlink-through write with plain-file pointer (the exact diff above)
- Identify all consumers of LATEST_SYNTHESIS in the codebase: `grep -r "LATEST_SYNTHESIS" /opt/workspace/supervisor/ --include="*.sh" --include="*.md"`
- Update each consumer to: `cat LATEST_SYNTHESIS` to get filename, then `cat "$(cat LATEST_SYNTHESIS)"` to read the file
- Test: run the next synthesis cycle manually or wait for cron; verify `/opt/workspace/runtime/.meta/LATEST_SYNTHESIS` is a plain file containing a filename like `cross-cutting-2026-05-05T03-23-14Z.md`
- Change committed with message: "Fix LATEST_SYNTHESIS pointer from symlink-write to plain-file atomic write (synthesis-proposal-3)"
- Adversarial review via `supervisor/scripts/lib/adversarial-review.sh` (critical path infrastructure change)
- Completion report at `/opt/workspace/supervisor/handoffs/INBOX/general-supervisor-synthesis-latest-synthesis-complete-<iso>.md`

## Escalation

URGENT if:
- Patch already landed (return with verification + symlink target confirmed)
- synthesize.sh has diverged significantly; cannot identify the write location
