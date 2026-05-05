---
from: synthesis-translator
to: general
date: 2026-05-04T03:30:30Z
priority: high
task_id: synthesis-fix-latest-synthesis-pointer
source_synthesis: /opt/workspace/runtime/.meta/cross-cutting-2026-05-04T03-26-05Z.md
source_proposal: Proposal 4 — Fix LATEST_SYNTHESIS pointer (cycle 2 repeat)
---

# Proposal 4 [HIGH, REPEAT — cycle 2]: Fix LATEST_SYNTHESIS pointer

Replace the symlink write with an atomic update.

## The problem

The LATEST_SYNTHESIS symlink is written through by `synthesize.sh`, overwriting
historical artifacts. The symlink still points to `cross-cutting-2026-04-29T15-24-48Z.md`,
but its content has been destroyed — the file now contains only a single line
pointing to `cross-cutting-2026-05-03T15-23-19Z.md`. When synthesis writes through
the symlink, it overwrites the old file's content. The Apr 29 synthesis content
is permanently lost. The pointer is stale and the mechanism is corrupted.

## Target change

**Exact change** (`/opt/workspace/supervisor/scripts/lib/synthesize.sh`):

Find the line that writes to LATEST_SYNTHESIS (currently line ~89):
```bash
echo "$OUTPUT_FILE" > "$WORKSPACE_LATEST_SYNTHESIS_PTR"
```

Replace with atomic plain-file write:
```bash
rm -f "$META_DIR/LATEST_SYNTHESIS"
printf '%s\n' "$OUTPUT_FILE" > "$META_DIR/LATEST_SYNTHESIS"
```

(Or equivalently: stop treating LATEST_SYNTHESIS as a symlink; make it a
plain file with atomic write.)

**Blast radius:** Synthesis pipeline only. Automatic. Fixes dispatch
gating for the executive.

## Verification before action (required)

- `ls -la /opt/workspace/runtime/.meta/LATEST_SYNTHESIS` — check current state
- `head -5 /opt/workspace/runtime/.meta/LATEST_SYNTHESIS` — check if it's pointing or containing a path
- `grep -n "LATEST_SYNTHESIS" /opt/workspace/supervisor/scripts/lib/synthesize.sh` — find the exact current line
- If the file is already a plain-text pointer (not a symlink), and the current synthesize.sh writes atomically, write completion report "already fixed" and skip

## Acceptance criteria

- `/opt/workspace/supervisor/scripts/lib/synthesize.sh` is updated to write atomically to LATEST_SYNTHESIS
- The symlink is removed (or overwritten with a plain file on the first run)
- After the fix, LATEST_SYNTHESIS is a plain text file containing the path to the current synthesis
- Change committed with message: "Fix LATEST_SYNTHESIS pointer corruption; replace symlink write with atomic plain-file update (synthesis Proposal 4)"
- No adversarial review required (straightforward pointer fix)
- Completion report at `runtime/.handoff/general-supervisor-synthesis-fix-latest-synthesis-pointer-complete-<iso>.md`

## Escalation

URGENT if:
- Primary verification reveals this is already fixed (obsolete)
- The current synthesize.sh uses LATEST_SYNTHESIS in a way that depends on symlink behavior (surface the specific usage)
