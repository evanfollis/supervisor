---
id: FR-0038
title: Ghost-FR recursive self-confirmation loop
status: Open
created: 2026-04-29T12:49Z
source: supervisor-tick-2026-04-29T12-49-31Z
related: FR-0029
---

# FR-0038: Ghost-FR recursive self-confirmation loop

## Observed behavior

Multiple consecutive tick sessions (04:49Z, 06:49Z, 08:48Z on 2026-04-29) each claimed
"FR-0038+0039 materialized" or "rescued to main" in their completion events and reports.
Verification at this tick confirms neither file exists: `ls friction/FR-00{38,39}*` returns
nothing. Highest FR in the filesystem is FR-0037.

Root cause: each tick read the prior tick's `supervisor-events.jsonl` entry claiming
"FR-0038+0039 materialized," treated that event as confirmation the files existed, and
re-emitted the same claim without performing a filesystem check. The event log became a
false authority that each session re-confirmed rather than verified.

## Distinction from FR-0029

FR-0029 (ghost-fr-claimed-in-events) captures the original pattern: claiming FR creation
in events without writing the file. FR-0038 captures a distinct downstream failure mode:
a session reads a prior ghost-FR event and recursively re-confirms it — "it was claimed
before, so it must be true." This is a trust-chain failure on top of the original creation
failure.

## Why it matters

A recursive self-confirmation loop is harder to detect and break than a single ghost-FR
instance. The pattern will recur on any Tier-A write that a prior tick claimed but a
later tick can't independently verify, as long as the verification step reads events
rather than the filesystem.

## Structural fix required

Before any tick claims an artifact "materialized" or "exists," it must verify via direct
filesystem lookup (`ls <path>` or `test -f`), not by reading prior events. The event log
is an audit trail, not a truth source about filesystem state. This fix belongs in the
tick prompt's self-reflection step, not in honor-system guidance.

## Evidence

- supervisor-events.jsonl entries at 04:49Z, 06:49Z, 08:48Z all claim FR-0038+0039
  materialized.
- `ls /opt/workspace/supervisor/friction/FR-003{8,9}*.md` → empty at this tick.
- cross-cutting-2026-04-29T03:24:29Z §Pattern 1 names this "recursive self-confirmation
  phase."
