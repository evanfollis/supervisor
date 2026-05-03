---
name: FR-0041 — Synthesis dispatch obligation expired 11 consecutive cycles with 0 proposals landed
status: Open
filed: 2026-05-03
source: cross-cutting-synthesis (11 consecutive windows, 2026-04-26 → 2026-05-03)
---

# FR-0041 — Synthesis dispatch obligation expired 11 consecutive cycles with 0 proposals landed

## Pattern

The workspace CLAUDE.md requires dispatched project handoffs within 24h of each synthesis
output (or an explicit deferral in `decisions/`). Over 11 consecutive synthesis cycles
(2026-04-26 through 2026-05-03T02:27Z), 0 synthesis proposals have landed as code changes,
ADR acceptances, or playbook amendments. The 24h dispatch obligation has expired in each cycle.

## Evidence

- `cross-cutting-2026-05-02T15-27-50Z.md` "Standing recommendations" table: 19 unique proposals,
  0 implemented. 8+ INBOX copies exist for the iterate-patch-freeze proposal alone.
- No `synthesis_reviewed` event appears in `events/supervisor-events.jsonl` since Apr 26.
- INBOX grew from 0 → 50 items over 11 cycles with no corresponding action.
- Estimated API cost: $20–40 in synthesis calls producing 0 codebase changes.

## Root cause

Three dispatch paths exist: (a) attended principal sessions, (b) autonomous tick sessions,
(c) handoff-to-general-session pipeline. Path (a) inactive during synthesis cycles (no human
sessions). Path (b) blocked by Tier-C restrictions on `scripts/lib/` and CLAUDE.md. Path (c)
marks handoffs `.done` without implementing changes — the general tick session reads handoffs
but has the same Tier-C restrictions.

The workspace has no path from synthesis proposal → implementation without human presence
for Tier-C (infrastructure) changes.

## Why it matters

The synthesis loop is the workspace's primary mechanism for cross-project friction discovery
and policy improvement. If proposals never land, the loop is a $20–40/cycle diagnostic
report generator with no execution path. It is producing increasingly precise diagnoses
of the same structural gap.

## Fix candidates

1. **Tier-B-auto classification** (proposed in synthesis-2026-05-02T15-27-50Z Proposal 5):
   Allow attended tick sessions to apply additive, 2+ cycle, infrastructure-only, no-ADR
   changes to `scripts/lib/`. Requires CLAUDE.md amendment (principal decision).

2. **Attended triage sessions**: Principal reviews and bulk-disposes INBOX items when available.

3. **Narrow scope**: Principal pre-approves specific pending changes (e.g., reflect.sh Write
   fix, synthesize.sh size gate) to unblock the immediate queue.

## Status

Open. Principal decision required for Fix 1. Proposal in INBOX:
`proposal-tier-b-auto-authority-2026-05-02T18-50Z.md`.
