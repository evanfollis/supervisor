---
priority: urgent
created: 2026-04-25T18:47Z
source: supervisor-tick-2026-04-25T18-47-34Z
fr: FR-0038
---

# URGENT — synthesis job writing empty stubs (2 consecutive runs)

Two consecutive synthesis runs produced 67-byte output files containing only the file's own path. Prior working syntheses were 14–22KB.

## Evidence

```
-rw-r--r--  18389  Apr 23  cross-cutting-2026-04-23T18-43-50Z.md
-rw-r--r--  22019  Apr 24  cross-cutting-2026-04-24T03-26-55Z.md
-rw-r--r--  14457  Apr 24  cross-cutting-2026-04-24T15-23-45Z.md
-rw-r--r--     67  Apr 25  cross-cutting-2026-04-25T03-27-27Z.md  ← stub
-rw-r--r--     67  Apr 25  cross-cutting-2026-04-25T15-28-05Z.md  ← stub
```

The 15:28Z run consumed 36s CPU and exited clean per journalctl — the synthesis harness ran but produced no real content.

## Downstream damage

The synthesis-translator (15:42Z) cited the empty stub as `source_synthesis` and filed 3 HIGH-priority INBOX proposals. Those proposals appear plausible (matching carry-forward patterns) but their provenance is suspect — they may have been generated from the translator's own prior knowledge rather than a live synthesis read.

The 3 INBOX proposals remain valid for implementation (reflect.sh verbose logging, governance event auto-emit, doctor ADR-review check) but should be evaluated independently of the stub-sourced synthesis.

## Action required

1. Read `scripts/lib/workspace-synthesize.sh` — identify where the synthesis output is captured and how the output file is written
2. Determine root cause (output redirect bug vs. Opus session exiting early vs. harness change)
3. Fix the output capture path
4. Add a guard: if output file <1KB after synthesis run, emit `synthesis_failed` event and do NOT let the translator job run
5. Verify the next synthesis run (03:23 or 15:23 UTC) produces substantive content

Full analysis: `friction/FR-0038-synthesis-job-writing-empty-stubs.md`
