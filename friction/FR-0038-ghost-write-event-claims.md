# FR-0038: Ghost-write event claims — tick branches not merged to main

Captured: 2026-05-01T18:47Z
Source: supervisor-tick
Status: open

## What happened

Tick sessions write Tier-A governance artifacts (friction records, active-issues
updates) and emit events claiming success, but those writes land on tick branches
(e.g. `ticks/2026-05-01-18`) that are never merged to main. From main's
perspective, the files don't exist. The same FRs get re-discovered and
re-reported each tick cycle.

The synthesis has flagged this for 9+ cycles as Pattern 2 (ghost-write). The
16:48Z tick note "verified on disk after write" was true — the file existed on
the tick branch at commit time, but the branch was never merged.

## Why it matters

The event model is not a truth source for main-branch state. Any consumer
(meta-scan, executive, synthesis) that trusts event claims without checking
main will draw false conclusions. Governance artifacts — especially FRs and
active-issues updates — become invisible from main until an attended session
merges the tick branches.

## Root cause / failure class

The tick wrapper commits to a tick branch, not main. There is no auto-merge
path from tick branches to main. Doctor reports aged tick branches as WARNs
but does not auto-merge. The INBOX has had a playbook proposal
(`proposal-merge-tick-branches-playbook`) for 137h+ without disposition.

## Fix needed

Option A: Tick wrapper auto-merges Tier-A changes to main before pushing tick
branch.
Option B: Ticks write directly on main (no branching for Tier-A Tier supervisor
writes).
Option C: Attended session periodically merges aged tick branches.

This FR is itself written on main by the 20:49Z tick (first successful main
write of this record).

## Remaining work

Choose option A, B, or C. Until then, every tick must re-create FRs that
prior ticks already wrote — the effective history is only visible in tick
branches, not in the canonical substrate.
