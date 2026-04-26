---
name: FR-0038 — synthesis job writing empty stubs
description: workspace-synthesize.timer produces 67-byte output files containing only the file path, not substantive synthesis content
status: Open
created: 2026-04-25T18:53Z
discovered-by: supervisor-tick-2026-04-25T18-47-34Z
---

# FR-0038 — Synthesis job writing empty stubs

## Status: Open

## Observed behavior

Two consecutive synthesis runs (2026-04-25T03:27Z and 2026-04-25T15:28Z) produced 67-byte output files containing only the output path. Prior working runs were 14–22KB.

```
-rw-r--r--  14457  Apr 24  cross-cutting-2026-04-24T15-23-45Z.md
-rw-r--r--     67  Apr 25  cross-cutting-2026-04-25T03-27-27Z.md  ← stub
-rw-r--r--     67  Apr 25  cross-cutting-2026-04-25T15-28-05Z.md  ← stub
```

The harness consumed 36s CPU and exited clean — the synthesis session ran but produced no real content.

## Downstream damage

The synthesis-translator (2026-04-25T15:42Z) cited the empty stub as `source_synthesis` and filed 3 HIGH-priority INBOX proposals from its own prior knowledge rather than live synthesis content. Those proposals are marked suspect-provenance. Additionally, synthesis has now been dark for 43h+ (as of 02:48Z 2026-04-26).

## Root cause hypothesis

Output redirect bug in `scripts/lib/workspace-synthesize.sh` OR Opus session exiting early before writing substantive content. The harness run duration (36s) suggests an early exit rather than a silent hang.

## Fix required

1. Read `scripts/lib/workspace-synthesize.sh` — identify where synthesis output is captured and how the output file is written.
2. Add a guard: if output file <1KB after synthesis run, emit `synthesis_failed` event and do NOT let the translator job run.
3. Verify the next synthesis run (03:23 or 15:23 UTC) produces substantive content.

Tier C work — requires attended session with scripts/lib/ write access.
