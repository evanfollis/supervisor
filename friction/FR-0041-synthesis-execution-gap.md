---
id: FR-0041
title: 11 synthesis cycles, 0 of 40 proposals implemented
status: Open
filed: 2026-05-02
source: cross-cutting synthesis 2026-05-02T03:23:48Z
severity: high
---

# FR-0041 — Synthesis execution gap: 11 cycles, 0/40 proposals

## Observed behavior

As of 2026-05-02T12:49Z, the synthesis/execution pipeline shows:
- 11 completed synthesis cycles (roughly 2 weeks of 12h cadence)
- 40 proposals in `handoffs/INBOX/`
- 0 proposals implemented, accepted as ADRs, or recorded as won't-fix
- Synthesis dispatch obligation (24h from synthesis → dispatched handoff or deferral) violated
  for the 2026-05-01T15:28Z synthesis (deadline ~2026-05-02T15:28Z)

## Why this matters

The synthesis/reflection loop is supposed to be a work queue, not a diagnostic archive.
High-fidelity diagnosis with zero execution is strictly worse than lower-fidelity diagnosis
with some execution — the queue grows, signal quality degrades, and the escalation surface
becomes noise.

## Root cause

1. **Tier-C gating**: Most proposals touch `scripts/lib/`, `.reviews/`, `CLAUDE.md` —
   all Tier-C from tick sessions. Ticks cannot implement them.
2. **No triage authority**: Tick sessions can't bulk-close proposals as won't-fix (that
   is attended-session work per ADR-0014).
3. **Attended sessions don't triage**: When the principal attaches, immediate project work
   takes priority over INBOX triage. The 24h dispatch obligation has no enforcement gate.

## Fix needed

One of:
A. **Grant ticks Tier-B authority** for low-risk proposals (documentation, playbooks, non-scripts).
   Requires ADR amendment.
B. **Mandatory attended-session INBOX sweep** — charter rule requiring the executive to
   dispose ≥5 INBOX items before starting any new work. Requires CLAUDE.md amendment.
C. **Terminal disposal**: Proposals aged >7 days without disposition are auto-archived
   as "deferred-indefinitely" with no further action. Requires synthesis job patch (Tier-C).

## Related

- INBOX: `URGENT-inbox-proposal-saturation-2026-04-28T08-50Z.md`
- Synthesis: `cross-cutting-2026-05-02T03-23-48Z.md` Pattern 4
- Dispatch obligation: `supervisor/CLAUDE.md §Automated Self-Reflection Loop`
