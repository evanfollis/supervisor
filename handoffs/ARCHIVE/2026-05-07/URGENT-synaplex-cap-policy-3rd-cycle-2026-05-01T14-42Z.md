---
type: URGENT
created: 2026-05-01T14:42Z
source: reflection-job-synaplex-2026-05-01T14-42-52Z
priority: urgent
project: synaplex
references:
  - /opt/workspace/supervisor/handoffs/INBOX/synaplex-cap-policy-decision-2026-04-30T14-49Z.md
  - /opt/workspace/runtime/.handoff/general-synaplex-cap-policy-decision-2026-04-30T15-00Z.md
carry_forward_cycles: 3
---

# URGENT: Synaplex cap policy — 3rd-cycle escalation

This observation has been reported in 3 consecutive reflection cycles
(2026-04-30T14:27, 2026-05-01T02:45, 2026-05-01T14:42) without a fix
commit, decision verdict, or `verified` pointer. Per workspace carry-
forward escalation rule (CLAUDE.md §Carry-forward escalation), this
must trigger an URGENT INBOX handoff.

## What's blocking

ADR-0029 §6 says "max 200 per source per day." The implementation does
"max 200 per fetch" with union accumulation. HN is now at 277 items for
2026-05-01 by 12:20Z and will reach ~400 by midnight. No data corruption,
but doc/code diverge.

The `high`-priority entry
(`synaplex-cap-policy-decision-2026-04-30T14-49Z.md`) has been in INBOX
since 2026-04-30T14:49Z (~24h) without action or deferral.

## Decision needed (unchanged)

**A** — Truncate post-merge by score  
**B** — Truncate post-merge by recency  
**C** — Ratify per-fetch semantic; amend ADR-0029 §6 wording ← **recommended**

## Additional urgency factor

Synaplex scoring cron fires hourly (12× per day). Intake fires every 4h
(3× per day). Nine of twelve score runs re-score an unchanged corpus.
With heuristic scoring this is free; with Sonnet scoring (activated when
ANTHROPIC_API_KEY lands) this is ~9 wasted full-corpus API calls per day.
**If the key is imminent, the score cron cadence must be fixed before it
lands.** This is a separate decision from cap policy but shares the same
"needs principal decision" gate. See reflection P1.
