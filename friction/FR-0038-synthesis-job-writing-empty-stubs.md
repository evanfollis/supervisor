---
id: FR-0038
title: synthesis job writing empty stubs (path-only output)
status: Open
created: 2026-04-25T18:47Z
source: supervisor-tick-2026-04-25T18-47-34Z
---

# FR-0038 — synthesis job writing empty stubs

## Observed

Two consecutive synthesis runs produced 67-byte output files containing only the file's own path:

```
/opt/workspace/runtime/.meta/cross-cutting-2026-04-25T03-27-27Z.md
/opt/workspace/runtime/.meta/cross-cutting-2026-04-25T15-28-05Z.md
```

Prior working syntheses (Apr 23–24) were 14–22KB. File sizes:
- `cross-cutting-2026-04-23T18-43-50Z.md`: 18,389 bytes
- `cross-cutting-2026-04-24T03-26-55Z.md`: 22,019 bytes  
- `cross-cutting-2026-04-24T15-23-45Z.md`: 14,457 bytes
- `cross-cutting-2026-04-25T03-27-27Z.md`: **67 bytes** ← stub
- `cross-cutting-2026-04-25T15-28-05Z.md`: **67 bytes** ← stub

## Downstream damage

The synthesis-translator job ran on the 15:28Z stub and produced three INBOX proposals (HIGH priority), citing the stub as their `source_synthesis`. The proposals contain plausible content (matching known carry-forward patterns), but it's unclear whether they were generated from prior-tick content or hallucinated from the empty stub. The proposals are in INBOX and deferred to attended session — but their provenance is suspect.

## Root cause (hypothesis)

Unknown. Possible causes:
1. The Opus session that runs synthesis is outputting ONLY the output filename (perhaps a bug in how the session startup script sets up the output redirect)
2. The synthesis job exited early (context limit, error) and the stub file was written by the wrapper script as a placeholder
3. A change in how `workspace-synthesize.service` handles the output file path

`journalctl` shows the Apr 25 15:28Z run consumed 36 seconds CPU and exited successfully — it did not error. This favors option 1 or a harness-level output handling change.

## FR collision note

The tick branch `ticks/2026-04-20-22` (unmerged) also has an `FR-0038-current-state-uncommitted-after-reflection.md`. When that branch is resolved, attended session must renumber one of the two FR-0038 files.

## Resolution needed

1. Read `scripts/lib/workspace-synthesize.sh` to understand how output is captured
2. Check the Opus session output path — is it writing its response to a file, and if so, does the harness redirect correctly?
3. Fix the output capture bug
4. After fix, verify next synthesis run produces substantive content
5. Add a check to the synthesis job: if output file is <1KB, treat as failure and escalate
