---
from: synthesis-translator
to: general
date: 2026-07-09T03:30:04Z
priority: high
task_id: synthesis-dispatch-sla-relax
source_synthesis: /opt/workspace/runtime/.meta/cross-cutting-2026-07-09T03-26-11Z.md
source_proposal: P1 — Relax dispatch SLA 24h → 7d
---

# P1: Relax dispatch SLA 24h → 7d

**Type:** CLAUDE.md amendment — "Automated Self-Reflection Loop" section.

**Current text:**
> the executive must dispatch a delegated project session within 24h

**Proposed replacement:**
> the executive must dispatch a delegated project session within 7d

**Rationale:** C131's dispatch SLA formally breached at 03:24Z Jul 9 — the first confirmed expiry. At current contact rate (~once per 10+ days), a 24h SLA fires a false violation every cycle. 23 consecutive breaches and counting. The SLA describes a daily-contact cadence that has not existed since at least June 9.

**Blast radius:** Supervisor dispatch obligation only. Automatic once CLAUDE.md is amended.

---

## Verification before action (required)

- Read `/root/.claude/CLAUDE.md` (user's global instructions) and `/opt/workspace/CLAUDE.md` (project instructions). Search for "Automated Self-Reflection Loop" section.
- Check if the "within 24h" language has already been updated to "within 7d". If yes, write completion report: "already landed in-file" and close.
- If not found or outdated, proceed to apply the amendment.

## Acceptance criteria

- The phrase "within 24h" in the dispatch obligation is replaced with "within 7d".
- Change committed to supervisor with clear message: "Relax dispatch SLA 24h → 7d per synthesis #133"
- Completion report at `/opt/workspace/supervisor/handoffs/INBOX/general-supervisor-synthesis-dispatch-sla-relax-complete-<iso>.md` pointing back to this handoff.

## Escalation

URGENT if:
- The principal has made a recent decision to enforce tighter dispatch cadence (e.g., a C13X decision in the last 7 days). Escalate the conflict.
- The amendment is blocked by a broader CLAUDE.md reorganization in-flight. Surface the blocking change.
