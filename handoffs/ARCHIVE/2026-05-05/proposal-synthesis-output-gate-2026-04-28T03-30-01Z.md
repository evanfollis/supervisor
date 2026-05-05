---
from: synthesis-translator
to: general
date: 2026-04-28T03:30:01Z
priority: high
task_id: synthesis-synthesis-output-gate
source_synthesis: /opt/workspace/runtime/.meta/cross-cutting-2026-04-28T03-25-05Z.md
source_proposal: Proposal 2 — Shared primitive — synthesis output size gate for synthesize.sh
---

# Shared primitive — synthesis output size gate for synthesize.sh

**Type:** Shared primitive fix.

This is the 5th cycle proposing this. The proposal is simple and the failure is actively degrading the meta-loop (3 of 6 runs producing stubs). The synthesis at 15:27Z Apr 27 produced a 67-byte stub; LATEST_SYNTHESIS has been corrupt for 11+ hours.

**Proposed change** in `/opt/workspace/supervisor/scripts/lib/synthesize.sh`:

After writing the output file (around line 59), add a size check before updating the LATEST_SYNTHESIS pointer:

```bash
OUTPUT_SIZE=$(wc -c < "$OUTPUT_FILE")
if [ "$OUTPUT_SIZE" -lt 500 ]; then
  echo "synthesize: WARNING — output is ${OUTPUT_SIZE} bytes (< 500), not updating LATEST_SYNTHESIS" >&2
  # Optionally write a friction event
  exit 0
fi
ln -sf "$OUTPUT_FILE" "$WORKSPACE_LATEST_SYNTHESIS_PTR"
```

Currently line 89 unconditionally updates LATEST_SYNTHESIS. The gate prevents corrupt pointers from propagating to the general session.

**Blast radius:** Synthesis job only. Automatic. Prevents corrupt LATEST_SYNTHESIS pointers. Does not fix why the synthesis sometimes produces stubs — but stops the failure from propagating.

## Verification before action (required)

- Check `synthesize.sh` line 89 — confirm it currently does `ln -sf "$OUTPUT_FILE" "$WORKSPACE_LATEST_SYNTHESIS_PTR"`
- Verify the size gate is not already present (grep for "OUTPUT_SIZE" or "500")
- Check if `$WORKSPACE_LATEST_SYNTHESIS_PTR` is defined in the script (should be `$META_DIR/LATEST_SYNTHESIS` or similar)

## Acceptance criteria

- Size gate logic added between the file-existence check (line 59) and the LATEST_SYNTHESIS pointer update
- Change committed with a message explaining the 4-cycle carry-forward and the propagation risk
- Adversarial review recommended (structural change to the meta-loop itself)
- Completion report at `runtime/.handoff/general-synthesis-synthesis-output-gate-complete-<iso>.md`

## Escalation

URGENT if:
- The size gate is already present in synthesize.sh
- The pointer-update variable name differs from what the proposal assumes
