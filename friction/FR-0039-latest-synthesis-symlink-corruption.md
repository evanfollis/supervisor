---
id: FR-0039
name: LATEST_SYNTHESIS symlink stale — synthesize.sh follows symlink when writing, corrupts historical files
created: 2026-04-29T02:49Z
source: supervisor-tick-2026-04-29T02-49-55Z
severity: high
status: open
---

# FR-0039: LATEST_SYNTHESIS symlink corruption — synthesize.sh overwrites historical artifacts

## What happened

The `LATEST_SYNTHESIS` symlink at `/opt/workspace/runtime/.meta/LATEST_SYNTHESIS` was pointing to `cross-cutting-2026-04-28T03-25-05Z.md` while the actual newest synthesis was `cross-cutting-2026-04-28T15-28-05Z.md`. Corrected this tick (2026-04-29T02:49Z).

The server-maintenance report (2026-04-29T01:27:35Z) notes the deeper structural issue: `synthesize.sh` follows the symlink when writing the output path. This means that if `LATEST_SYNTHESIS` is a symlink, the synthesis job writes new content *through* the symlink, overwriting the historical artifact that LATEST_SYNTHESIS was pointing to rather than creating a new timestamped file.

## Pattern

- Multiple synthesis runs produced 67-byte stubs (2 of 3 intervening cycles between Apr 26–28)
- Synthesis proposals never land because synthesis output is often corrupt/truncated
- Meta-loop is partially broken: reflections run correctly, synthesis sometimes doesn't persist

## Impact

- `LATEST_SYNTHESIS` dispatch decisions are sometimes based on 2+ cycle old synthesis
- Historical synthesis files may be silently overwritten (data loss of diagnostic output)
- 0 of 9 cross-cutting proposals landed across 4 substantive synthesis cycles (Apr 26–28)

## Required fix

In `scripts/lib/synthesize.sh`:
- Write output to the timestamped file first; use `ln -sf` to update `LATEST_SYNTHESIS` after successful write
- Add a size gate: if the synthesis output is < N bytes (e.g. 500), treat as a failure, do not overwrite LATEST_SYNTHESIS
- Verify: `wc -c` on the output before committing the symlink update

Tier C change — requires attended session.

## Workaround applied this tick

Symlink manually updated to `cross-cutting-2026-04-28T15-28-05Z.md`. This is a per-tick workaround; the structural fix requires changes to `synthesize.sh`.
