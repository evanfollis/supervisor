---
id: FR-0038
title: Ghost FR materialization — tick branches claim FRs that never land on main
status: Open
severity: HIGH
detected: 2026-04-27T18:47Z
source: supervisor-tick
---

# FR-0038: Ghost FR materialization

## What happened

Tick sessions on branches (`ticks/YYYY-MM-DD-HH`) emit `fr_captured` events claiming to have
written friction records (e.g., FR-0038–0041 per events at 2026-04-27T08:49Z). The tick wrapper
commits those files to the tick branch, which is never merged to main. On main, the highest FR
that exists is FR-0037. Events say FR-0038–0041 exist; `ls friction/` shows they don't.

Concrete evidence: The 16:49Z tick event claims `fr_captured` for
`friction/FR-0038-synthesis-output-empty-file.md`. That file does not exist on main. The FR number
was consumed, the event was emitted, but the record is unreachable and the next tick correctly
writing FR-0038 would appear to be a duplicate.

## Why it matters

- FR numbers in `supervisor-events.jsonl` become misleading — events reference files that don't exist
- The friction record discipline (required by ADR-0013) is structurally broken for tick-session work
- Every synthesis that reads friction surface misses entire classes of captured observations
- Escalation detection that scans by FR count will produce wrong results

## Root cause

Tick branches are not merged to main. Tier-A writes during a tick session land on the tick branch,
not on main. The autocommit runs on main but only fires every ~2h; it commits Tier-A changes made
directly on main but cannot reach tick-branch content.

## Required fix (Tier-C — attended exec session)

Two options:
1. Tick wrapper auto-merges Tier-A paths (friction/, events/, handoffs/) from the tick branch to main
   after the tick session completes.
2. Ticks are restructured to run directly on main for Tier-A file writes, with the tick report
   committed separately to the tick branch.

Either requires changes to `supervisor-tick.sh` (Tier-C). The existing merge-tick-branches playbook
proposal in INBOX (`proposal-merge-tick-branches-playbook-2026-04-26T03-37-07Z.md`) is related.
