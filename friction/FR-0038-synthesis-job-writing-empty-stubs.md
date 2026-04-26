---
name: FR-0038 — synthesis job writing empty stubs
description: workspace-synthesize.timer produced 67-byte output files containing only the file path, not substantive synthesis content
status: Resolved (synthesis working as of 2026-04-26T03:26Z; structural guard not yet implemented)
created: 2026-04-25T18:53Z
discovered-by: supervisor-tick-2026-04-25T18-47-34Z
---

# FR-0038 — Synthesis job writing empty stubs

## Status: Resolved (structural guard still pending)

## Observed behavior

Two consecutive synthesis runs (2026-04-25T03:27Z and 2026-04-25T15:28Z) produced 67-byte output files containing only the output path. Prior working runs were 14–22KB.

```
-rw-r--r--  14457  Apr 24  cross-cutting-2026-04-24T15-23-45Z.md
-rw-r--r--  22019  Apr 24  cross-cutting-2026-04-24T03-26-55Z.md
-rw-r--r--     67  Apr 25  cross-cutting-2026-04-25T03-27-27Z.md  ← stub
-rw-r--r--     67  Apr 25  cross-cutting-2026-04-25T15-28-05Z.md  ← stub
-rw-r--r--  22485  Apr 26  cross-cutting-2026-04-26T03-26-05Z.md  ← recovered
```

The 2026-04-26T03:26Z synthesis run produced 22KB of substantive content — the immediate problem resolved.

## Downstream damage

The synthesis-translator (2026-04-25T15:42Z) cited the empty stub as `source_synthesis` and filed 3 HIGH-priority INBOX proposals from its own prior knowledge. Those proposals are marked suspect-provenance. The 36h synthesis gap (2026-04-24T15:23Z → 2026-04-26T03:26Z) left the workspace without cross-cutting analysis.

## Root cause hypothesis

Output redirect bug in `scripts/lib/workspace-synthesize.sh` OR Opus session exiting early before writing substantive content. The harness run duration (36s) suggests an early exit rather than a silent hang.

## Structural fix still required (INBOX: proposal-synthesis-output-size-gate)

1. Add a size guard: if output file <1KB after synthesis run, emit `synthesis_failed` event and do NOT update `LATEST_SYNTHESIS` or trigger the translator job.
2. Proposal in INBOX: `proposal-synthesis-output-size-gate-2026-04-26T03-37-07Z.md`.

Tier C work — requires attended session with scripts/lib/ write access.
