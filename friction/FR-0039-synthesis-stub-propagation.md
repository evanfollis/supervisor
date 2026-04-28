---
id: FR-0039
title: Synthesis stub propagation — LATEST_SYNTHESIS points to 67-byte stub for 4+ consecutive cycles
status: Open
created: 2026-04-28
observed-by: supervisor-tick (multiple cycles 2026-04-28)
---

# FR-0039: Synthesis stub propagation

## Observed pattern

The synthesize.sh job is producing a 67-byte stub file containing only the filename as content, rather than an actual synthesis. LATEST_SYNTHESIS has pointed to this stub for at least 4 consecutive synthesis cycles (2026-04-28T03:25Z confirmed stub). The translator job reads the stub, finds no actionable proposals, and generates carry-forward observations — which are also stubs or minimal content.

## Root cause

The `synthesize.sh` script likely hits a Claude invocation failure, timeout, or output-size error silently. Without a size gate, a 67-byte "output" is treated as a successful synthesis. The carry-forward loop then operates on stubs, producing more stubs.

## Why it matters

- The reflection/synthesis meta-loop is completely stalled. Actual cross-cutting observations from per-project reflections are never being synthesized.
- Tick sessions that read the synthesis and find nothing new do not generate new proposals — the backlog appears healthy but is actually stale.
- The `proposal-synthesis-output-gate-2026-04-28T03-30-01Z.md` INBOX proposal directly addresses this with a 5-line bash fix to `scripts/lib/synthesize.sh`.

## Fix

Add a size gate to `synthesize.sh`: if the output file is smaller than N bytes (e.g. 500), treat it as a failed synthesis and do not update LATEST_SYNTHESIS. This is a Tier-C change (scripts/lib/) requiring an attended session.

See INBOX proposal: `proposal-synthesis-output-gate-2026-04-28T03-30-01Z.md`

## Resolution

Pending attended session to implement the size gate in `scripts/lib/synthesize.sh`.
