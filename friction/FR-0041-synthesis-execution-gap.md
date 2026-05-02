---
id: FR-0041
title: Synthesis-to-execution pipeline non-functional — 0 of 40 proposals landed in 11 cycles
status: Open
created: 2026-05-02
severity: high
projects: supervisor, all
---

# FR-0041: Synthesis-to-execution pipeline non-functional

## What happened

11 consecutive synthesis cycles (starting ~2026-04-21) have produced proposals. As of
2026-05-02T03:23Z, zero of those proposals have been implemented in any project. INBOX
has grown from 0 to 40 items (40 unacted proposals). The synthesis loop produces
high-fidelity diagnosis but zero execution — the diagnostic surface is working while
the execution surface is structurally blocked.

## Root cause

Almost all proposals target Tier-B or Tier-C surfaces (scripts/lib/, CLAUDE.md, existing
ADR files), which tick sessions cannot touch. The only path to implementation is:
1. An attended principal session manually triaging and implementing
2. Tick sessions being granted authority for safe Tier-B changes

Neither path has been activated. The attended session has not triaged proposals in 6+
days. The authority question ("should ticks implement Tier-B proposals?") was raised in
the May 1 synthesis but not answered.

## Why this matters

The reflection/synthesis loop exists to drive workspace improvement. If proposals never
land, the loop is a cost center (CPU + API credits) with no return. The INBOX has grown
to 40 items and continues growing ~4/cycle. Signal quality degrades as urgent items
compete with 40 unactioned background proposals.

## Fix

Option A: Attended session bulk-triages INBOX. Even bulk "won't-fix" restores URGENT
signal quality. One 30-minute session could clear 30+ proposals.

Option B: Grant tick sessions authority to implement clearly safe Tier-B proposals
(e.g., synthesis-translator dedup gate, post-reflect CURRENT_STATE auto-commit) without
attended approval. Define "safe" criteria in an ADR.

## References

- Synthesis pattern 4: cross-cutting-2026-05-02T03-23-48Z.md
- INBOX: URGENT-inbox-proposal-saturation-2026-04-28T08-50Z.md
- First noted: cross-cutting-2026-04-26T (cycle 2)
