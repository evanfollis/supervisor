---
name: FR-0039
slug: fr-ghost-write-tick-branch-isolation
status: Open
created: 2026-04-30
source: supervisor-tick-2026-04-30T14-49-54Z
---

# FR-0039 — FR ghost-writes: tick sessions claimed file creation that never landed on main

## What happened

Starting 2026-04-30T02:49Z, supervisor events log reports creating FR-0038, FR-0039, FR-0040
across at least 6 tick attempts (02:49Z, 04:49Z, 06:48Z, 08:48Z and earlier). As of
2026-04-30T14:49Z, `ls friction/` ends at FR-0037 on main. The friction files never
landed.

The ghost-write pattern: tick sessions wrote files to their working tree, the wrapper
committed those files to a tick branch (`ticks/2026-04-30-NN`), the tick branch was never
merged to main, and the session event log claimed `friction/FR-003N written` as if it were
durable.

The 08:48Z tick explicitly wrote "FR-0038 landed for real (6th+ attempt, first to persist)"
in its session_reflected event — but it had not persisted to main.

## Why it matters

FR-0029 (ghost-FR-claimed-in-events) was written for the same failure class in a single
instance. FR-0039 documents the recurrence at scale: 6+ ghost-writes of the same 3 FRs
across multiple ticks, with increasing false confidence in events. The friction surface
becomes unreliable as a truth source.

Root: tick branches accumulate but are never merged. Any durable write by a tick must land
on a merged branch or on main directly to be real. Tick branches with governance artifacts
(friction files, active-issues updates) that remain unmerged are worse than not writing —
they produce ghost-events and mislead subsequent ticks into skipping re-writes.

## What would fix it

Two options:
1. Tick wrapper merges completed tick branches to main automatically (risky — merge conflicts
   possible if attended session is also writing).
2. Tick sessions that care about durability write to main directly (no tick branch) — which is
   what this session (14:49Z) is doing. The Tier-A writable surfaces are always written
   to main from this session type.

Attended session must decide: is the tick-branch model intentional isolation, or is it
producing false governance-artifact durability claims?

## Status

Open — structural. Proposal `proposal-tick-postaction-state-verification-2026-04-30T03-35-43Z.md`
in INBOX partially addresses this; needs attended session to extend the tick wrapper.
