---
name: FR-0043 — tick boundary-breach detector false positive on reflection-authored test files
status: Open
filed: 2026-05-23T06:48Z
source: supervisor-tick-2026-05-23T06-48-05Z
---

# FR-0043: Tick boundary-breach detector fires on reflection-authored test files

Status: open

## What happened

The tick at 2026-05-23T04:49:35Z produced URGENT-tick-boundary-breach with:
```
scripts/lib/.erofs-test-meta-reflection (matched scripts/lib/*, status=??)
scripts/lib/TEST_WRITE_2951547 (matched scripts/lib/*, status=??)
```

These files were created by the **meta-reflection job at 02:28:36Z** (confirmed in
`supervisor-reflection-2026-05-23T02-28-36Z.md` — the reflection ran a write test to
disprove the tick's EROFS assertion). The reflection job ran more than 2 hours before
the tick that flagged them.

The breach-detection logic reads `git status --porcelain` after the tick run and flags
any untracked/modified file matching `scripts/lib/*`. It does not verify that the tick
session itself created those files — it fires on pre-existing dirty tree state from
other processes.

## Impact

- Generates spurious URGENT-tick-boundary-breach handoffs
- The attended session is expected to investigate "tick Tier-C violations" that the tick
  didn't cause
- Consumes INBOX capacity under saturation suppression

## Root cause

The post-run dirty-tree check compares supervisor HEAD to dirty tree but does not
snapshot pre-run untracked state to distinguish files present before the tick ran from
files created during the tick.

## Fix (requires attended session — scripts/lib/ write)

In `scripts/lib/supervisor-tick.sh` (or its wrapper), before launching the tick session:
1. Capture pre-run untracked state: `git -C /opt/workspace/supervisor status --porcelain | grep '??' > /tmp/pre-tick-untracked`
2. After tick completes, diff against the pre-run snapshot; flag only *new* untracked entries.

Alternatively: add `scripts/lib/.erofs-test-*` and `scripts/lib/TEST_WRITE_*` to
`.gitignore` or a `.git/info/exclude` entry so test artifacts don't trigger the breach
detector at all.

## Why this is load-bearing

The EROFS write-test artifacts are diagnostic evidence — they prove scripts/lib/ is
writable from reflection/attended sessions (disproves the tick's EROFS assertion). If
the breach detector fires on them, those artifacts get treated as violations and are
likely to be deleted, destroying the primary evidence for the most consequential
open issue (reflect.sh:193 fix blocked by false EROFS claim).
