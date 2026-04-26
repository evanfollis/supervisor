---
name: Synthesis proposals target Tier-C files but no attended pickup is consuming them
status: open
severity: high
first_seen: 2026-04-26T22:47Z
source: supervisor-tick-2026-04-26T22-47-35Z
---

# FR-0041 — Synthesis→Tier-C execution gap

## Observation

11 proposals from synthesis cycles (2026-04-25T15:42Z, 2026-04-26T03:37Z, 2026-04-26T15:33Z) are sitting in `supervisor/handoffs/INBOX/` unexecuted. Every one of them targets `scripts/lib/` — Tier C (OS-read-only for unattended ticks). The proposals include critical and high-priority items (tick-event-labeling fix, CURRENT_STATE reflect-commit diagnostic, review-debt-scan). The oldest is 31h old.

Unattended ticks correctly identify these as Tier C and defer them. But there is no mechanism ensuring an attended session picks them up within a reasonable SLA.

## Root cause

The synthesis loop produces proposals and routes them to INBOX. The unattended tick loop correctly defers Tier-C work. But there is no attended-session trigger or escalation path that fires when Tier-C proposals age past a threshold. The attended executive session is the only execution path, and it's not opened on a predictable schedule.

## Impact

- Critical infrastructure fixes (FR-0038 root cause: tick event labeling) sit idle
- Active governance surfaces (active-issues.md on main) remain stale because the fix requires a Tier-C edit
- INBOX accumulates: currently 14 items, 11 proposals all awaiting attended pickup

## Related

- FR-0038: tick events falsely claim "on main" — the fix (supervisor-tick.sh edit) is Tier C
- FR-0039: consecutive tick invocation failures — fix is Tier C
- URGENT-escalated-adr-review-and-tick-branch-8-defers-2026-04-26T08-48Z.md

## Resolution path

1. Attended session opens and implements the critical/high proposals in INBOX (especially `proposal-tick-event-labeling`)
2. Consider: an URGENT escalation after 24h of unexecuted Tier-C proposals — the same age-check mechanic that fires for INBOX items
