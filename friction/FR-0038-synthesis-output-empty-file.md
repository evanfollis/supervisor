---
id: FR-0038
title: synthesis job produced empty/self-referential output file
status: Open
severity: HIGH
created: 2026-04-27T16:49Z
source: supervisor-tick-2026-04-27T16-49-30Z
---

# FR-0038 — Synthesis output file empty/self-referential

## Observation

The `workspace-synthesize.timer` job at 2026-04-27T15:27Z produced
`runtime/.meta/cross-cutting-2026-04-27T15-27-30Z.md` with 67 bytes of content:
only the file's own path as a string. `LATEST_SYNTHESIS` now points to this
empty file.

## Evidence

```
$ wc -l /opt/workspace/runtime/.meta/cross-cutting-2026-04-27T15-27-30Z.md
1
$ cat /opt/workspace/runtime/.meta/cross-cutting-2026-04-27T15-27-30Z.md
/opt/workspace/runtime/.meta/cross-cutting-2026-04-27T15-27-30Z.md
```

## Impact

- Synthesis cycle broken: no proposals generated from the 14:xx UTC reflections
- `LATEST_SYNTHESIS` pointer is corrupted — future sessions reading it see garbage
- Synthesis dispatch deadline enforcement cannot fire against an empty synthesis
- Any session that reads LATEST_SYNTHESIS as "the current synthesis" will get stale proposals from the 03:24Z file

## Root cause hypothesis

`synthesize.sh` likely initializes the output file with its own path as a
header (or echo), then the Claude invocation fails before writing actual content.
The file ends up containing only the initialization line.

## Fix class

Add a size gate in `synthesize.sh`: if output file is < 200 bytes after the
synthesis session, treat as failure, do not update `LATEST_SYNTHESIS`, and
write an URGENT INBOX item. (Proposal `proposal-synthesis-output-size-gate-2026-04-26T03-37-07Z.md` already in INBOX — this FR is the trigger evidence.)

## Status

Open. Tier-C fix (synthesize.sh). Attended session required.
