---
id: FR-0039
title: synthesis-stub-propagation
status: Open
created: 2026-04-28T04:50Z
observed-by: supervisor-tick-2026-04-28T04-50-02Z
---

# FR-0039: Synthesis stub propagates to LATEST_SYNTHESIS

## Pattern

The synthesis job (`synthesize.sh`) writes a file and unconditionally updates the `LATEST_SYNTHESIS` symlink, even when the output is a stub (67 bytes — essentially just the file path). The stub then propagates to every session that reads `LATEST_SYNTHESIS` as if it were a real synthesis.

## Evidence

- `cross-cutting-2026-04-28T03-25-05Z.md`: 67 bytes, contains only the file path.
- `cross-cutting-2026-04-27T15-27-30Z.md`: 67 bytes, contains only the file path.
- `LATEST_SYNTHESIS` → `cross-cutting-2026-04-28T03-25-05Z.md` (the stub).
- Synthesis-translator still generated 3 carry-forward proposals at 03:30Z, citing the 03:25Z stub as source, creating a false paper trail.
- Meta-reflection at 02:24Z flagged "LATEST_SYNTHESIS 67-byte stub 11h" as a critical drift.
- INBOX item `proposal-synthesis-output-gate-2026-04-28T03-30-01Z.md` is the 5th-cycle carry-forward proposing a fix to `synthesize.sh`.

## Root cause

`synthesize.sh` line 89 (per the proposal) unconditionally updates `LATEST_SYNTHESIS` after writing any output. No minimum size check prevents a stub from becoming the canonical pointer.

## Why this matters

The synthesis loop is the meta-level diagnostic channel. When LATEST_SYNTHESIS points to a stub, every session that reads it gets an empty brief. Worse, the synthesis-translator continues to generate INBOX proposals anyway (from carry-forward memory, not the stub content), creating the illusion of a functioning loop while the actual synthesis input is absent. Executive sessions may defer INBOX items as "synthesis-generated" when they are actually translator-generated carry-forwards without current-cycle grounding.

## Fix direction

Add a size gate in `synthesize.sh` after writing the output: if `wc -c < "$OUTPUT_FILE"` < 500 bytes, warn and do NOT update `LATEST_SYNTHESIS`. The fix is in `proposal-synthesis-output-gate-2026-04-28T03-30-01Z.md` (INBOX). This is a Tier-C edit; requires attended session.
