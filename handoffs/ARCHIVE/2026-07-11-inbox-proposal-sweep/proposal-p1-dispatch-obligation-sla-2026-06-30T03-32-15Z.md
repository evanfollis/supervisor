---
from: synthesis-translator
to: general
date: 2026-06-30T03:32:15Z
priority: high
task_id: synthesis-p1-dispatch-sla
source_synthesis: /opt/workspace/runtime/.meta/cross-cutting-2026-06-29T15-27-11Z.md
source_proposal: P1 - Relax dispatch obligation to match attended cadence
---

# P1: Relax dispatch obligation SLA from 24h to 7 days

## Full Proposal (from C114)

**Type:** CLAUDE.md amendment — "Automated Self-Reflection Loop" section, dispatch obligation paragraph.

**Current text:**
```
Synthesis proposals sitting >24h without dispatched action or recorded
deferral escalate as FR-class structural issues.
```

**Proposed replacement:**
```
Synthesis proposals sitting >7 days without dispatched action or recorded
deferral escalate as FR-class structural issues. The 7-day window
reflects the actual attended cadence of this workspace; a tighter SLA
produces breach noise rather than useful pressure when sessions are
less frequent.
```

**Rationale:** The 24h SLA has breached 3 consecutive times (C110, C111, C112) and will continue breaching indefinitely at current attendance patterns. The breach record is noise, not signal. A 7-day SLA would fire only when something is genuinely stale, and the synthesis-translator INBOX growth rate would drop to ~1-2 items/week instead of ~10/day.

**Blast radius:** Supervisor only (dispatch obligation enforcement). Automatic once CLAUDE.md is amended.

## Verification before action (required)

- Run `git log --oneline -20` on `/opt/workspace`. Check if this amendment has already landed via another path (commit message would reference P1, dispatch SLA, or 7 days).
- Read `/opt/workspace/CLAUDE.md` line 194 onward. Verify that it still contains `>24h` (not `>7 days`).
- If either check shows the change is already present, write a completion report stating "already landed" and close.

## Acceptance criteria

- Line 194 of `/opt/workspace/CLAUDE.md` (or nearby if line numbers shifted) is updated from `>24h` to `>7 days` with the full rationale text
- Change committed with message: "Relax dispatch obligation SLA to 7 days to match actual attended cadence" (or similar — explain the why)
- Completion report at `/opt/workspace/supervisor/handoffs/INBOX/general-p1-dispatch-sla-complete-<iso>.md` pointing back to this handoff and the source synthesis

## Escalation

URGENT if:
- Primary verification reveals this amendment has already landed. Write a completion report saying "obsolete — already landed at <commit SHA>" and close.
- The amendment conflicts with a more recent decision. Do not force-apply; escalate with the conflict named.
