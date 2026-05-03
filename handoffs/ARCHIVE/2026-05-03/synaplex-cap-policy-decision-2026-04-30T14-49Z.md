---
type: decision-needed
created: 2026-04-30T14:49Z
source: supervisor-tick-2026-04-30T14-49-54Z
priority: high
project: synaplex
references: /opt/workspace/runtime/.handoff/general-synaplex-cap-policy-decision-2026-04-30T15-00Z.md
---

# Synaplex Layer 1 cap policy — principal decision needed

5th carry-forward cycle. Original handoff at the reference path above has full context.
ADR-0029 §6 says "max 200 per source per day"; implementation does "max 200 per fetch"
with union accumulation producing 450 items/day for HN. No data corruption. Decision needed:

**A** — Truncate post-merge by score (requires scorer at truncation time)  
**B** — Truncate post-merge by recency (simple; penalizes late-trending content)  
**C** — Ratify per-fetch semantic; amend ADR-0029 §6 wording (0 code change; closes loop)

Synaplex recommendation: **C**. Layer 2 reasoning will filter anyway; truncating at Layer 1
is premature and daily file size is bounded (~hundreds/day for HN).

If C: executive amends `decisions/0029-…` §6 directly (Tier-A write).
If A or B: route to synaplex session for ~10–20 LOC implementation.
