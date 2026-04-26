---
id: FR-0038
title: Synthesis loop produces empty stub files instead of substantive output
status: Open
created: 2026-04-25T18:53Z
detected-by: supervisor-tick-2026-04-25T18-47-34Z
---

# FR-0038 — Synthesis loop produces empty stub files

## Observation

Two consecutive synthesis runs (2026-04-25T03:27Z and 2026-04-25T15:28Z) produced 67-byte files containing only the output path, not substantive synthesis content. `LATEST_SYNTHESIS` pointed at a stub for 36h. The downstream translation job ran against stubs and generated INBOX proposals from cached knowledge rather than live analysis.

## Impact

The workspace's highest-level feedback mechanism was dead for 3 cycles. Any governance surfaced by synthesis in that window was generated without real reflection input — phantom signal.

## Root cause hypothesis

The synthesis session exits early (possibly due to invocation failure or empty input) but still writes the output file with a minimal stub. No detection or INBOX diagnostic fires.

## Proposed fix class

- Synthesis wrapper should check output file size (>1KB minimum) before marking success.
- On stub detection, write `INBOX/URGENT-synthesis-stub-<iso>.md` and preserve the prior `LATEST_SYNTHESIS` pointer.

## Status

Open — synthesis is currently working (cross-cutting-2026-04-26T03-26-05Z.md is substantive), but no guard has been added to prevent recurrence.
