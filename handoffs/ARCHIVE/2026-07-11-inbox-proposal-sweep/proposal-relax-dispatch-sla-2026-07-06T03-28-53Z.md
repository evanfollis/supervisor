---
from: synthesis-translator
to: general
date: 2026-07-06T03:28:53Z
priority: high
task_id: synthesis-relax-dispatch-sla
source_synthesis: /opt/workspace/runtime/.meta/cross-cutting-2026-07-06T03-24-44Z.md
source_proposal: P1 — Relax dispatch SLA 24h → 7d
---

# Relax dispatch SLA 24h → 7d

## Proposal

**Type:** CLAUDE.md amendment — "Automated Self-Reflection Loop" section.

**Current text:**
```
the executive must dispatch a delegated project session within 24h
```

**Proposed replacement:**
```
the executive must dispatch a delegated project session within 7d
```

**Rationale:** The 24h SLA was calibrated for daily principal sessions. At current attachment rate (~1 session per 7+ days), it fires a false violation every cycle. 15 consecutive breaches degrade the escalation surface — a permanently-red indicator is no indicator.

**Blast radius:** Supervisor dispatch obligation only. Automatic once CLAUDE.md is amended.

## Verification before action (required)

- Check `/opt/workspace/CLAUDE.md` for the current text under "Dispatch obligation" (currently at line ~307). Verify the 24h SLA is still in place.
- If already amended to 7d, write a completion report stating "already landed" instead of re-applying.

## Acceptance criteria

- `/opt/workspace/CLAUDE.md` line mentioning dispatch SLA is updated from `within 24h` to `within 7d`
- Commit message: "Relax dispatch obligation SLA from 24h to 7d — current attachment rate (~1 session/7d) causes false-positive violations"
- Completion report at `runtime/.handoff/general-complete-relax-dispatch-sla-<iso>.md` pointing to this handoff

## Escalation

None expected. Purely textual amendment.
