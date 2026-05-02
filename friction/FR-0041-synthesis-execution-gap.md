---
id: FR-0041
title: Synthesis produces proposals; zero land — 11 cycles, 40+ items unimplemented
status: Open
created: 2026-04-25
updated: 2026-05-02
source: cross-cutting synthesis recurring observation
---

# FR-0041: Synthesis execution gap

## What happened

The workspace has run 11+ synthesis cycles. Every cycle produces cross-cutting
proposals. As of 2026-05-02, zero of 40+ proposals have been implemented or
formally dispositioned. The INBOX holds 40 items; most are Tier-B or Tier-C
changes that tick sessions cannot write.

## Why it matters

The reflection/synthesis loop is designed as a work queue, not a diagnostic
archive. When proposals accumulate without disposition, the loop degrades into
a read-and-file pattern — which produces the exact "80h perfect-diagnosis-zero-
execution" failure class the loop was designed to prevent. Synthesis quality is
high; execution pipeline is broken.

## Root causes

1. **Ghost-write pattern (FR-0038)**: tick sessions that tried to write Tier-A
   changes (FR records, active-issues updates) were on unmerged branches — their
   writes didn't land, so the queue appeared to grow
2. **Tier-C gate**: most proposals require scripts/lib/ or CLAUDE.md edits that
   ticks cannot write; no attended session has dispatched these
3. **Dispatch obligation not enforced**: the 24h dispatch obligation rule exists
   but the executive hasn't had an attended session in multiple days
4. **INBOX saturation**: with 40 items, each new proposal is noise against an
   already-unreadable backlog; the saturation exception fires but doesn't clear
   the backlog

## Fix direction

An attended session must run a bulk triage of the INBOX proposals:
- Most are Tier-C (scripts/lib/) changes that need a single attended operator pass
- Many are superseded by later formulations and can be closed as duplicates
- A few are genuine Tier-A items that the tick should have written but ghost-wrote

The backlog is a one-time attended-session problem, not a recurring structural one
(once the ghost-write bug is fixed and the triage runs, the queue should stay clear).
