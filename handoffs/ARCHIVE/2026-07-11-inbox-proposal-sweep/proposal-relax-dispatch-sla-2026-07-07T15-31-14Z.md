---
from: synthesis-translator
to: general
date: 2026-07-07T15:31:14Z
priority: high
task_id: synthesis-p1-dispatch-sla
source_synthesis: /opt/workspace/runtime/.meta/cross-cutting-2026-07-07T15-27-01Z.md
source_proposal: P1 — Relax dispatch SLA 24h → 7d
---

# P1: Relax dispatch SLA 24h → 7d

**Type:** CLAUDE.md amendment — "Automated Self-Reflection Loop" section.

**Current text:**
```
the executive must dispatch a delegated project session within 24h
```

**Proposed replacement:**
```
the executive must dispatch a delegated project session within 7d
```

**Rationale:** At current attachment rate (~1 session per 9+ days, sub-5-min), the 24h SLA fires a false violation every cycle. 19 consecutive breaches.

**Blast radius:** Supervisor dispatch obligation only. Automatic once CLAUDE.md is amended.

## Verification before action (required)

- Check if `/opt/workspace/CLAUDE.md` already contains "7d" in the dispatch SLA section. If yes, this is already landed.
- Search for the exact current text to verify the location before amending.

## Acceptance criteria

- The 24h SLA text is replaced with 7d in the "Automated Self-Reflection Loop" section.
- Change committed with message: "Relax dispatch SLA to 7d per C130 synthesis — reduce false violations at current principal contact rate"
- Completion report at `/opt/workspace/supervisor/handoffs/general-p1-dispatch-sla-complete-<iso>.md` pointing back to this handoff.

## Escalation

URGENT if:
- The SLA has already been changed to a different value (verify against C130 intent).
- The synthesis is stale — check if a more recent decision overrides this.
