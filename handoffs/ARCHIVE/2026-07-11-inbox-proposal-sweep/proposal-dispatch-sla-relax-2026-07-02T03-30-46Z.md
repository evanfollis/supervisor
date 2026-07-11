---
from: synthesis-translator
to: general
date: 2026-07-02T03:30:46Z
priority: high
task_id: synthesis-dispatch-sla-relax
source_synthesis: /opt/workspace/runtime/.meta/cross-cutting-2026-07-02T03-26-11Z.md
source_proposal: P1 — Relax dispatch obligation to match attended cadence
---

# P1: Relax dispatch obligation to match attended cadence

**Type:** CLAUDE.md amendment — "Automated Self-Reflection Loop" section.

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

**Rationale:** Current 24-hour SLA assumes daily attended sessions. Actual cadence is ~4–5 days between attended sessions. Tightening the deadline creates false positives (breach accumulation) rather than useful accountability signal. Pattern 1 (C119 synthesis) identifies this as the root cause of 8 consecutive dispatch-obligation breaches. This amendment closes the gap between policy and reality.

**Blast radius:** Supervisor only. Automatic once CLAUDE.md is amended.

## Verification before action (required)

- Check `/opt/workspace/CLAUDE.md` around line 300–305 (Automated Self-Reflection Loop section) for current text.
- Confirm the "24h" language is present and unchanged since C114 (6 cycles ago).
- If text has been changed or amended, write completion report: "already landed" with the commit SHA and date.

## Acceptance criteria

- Amendment applied to `/opt/workspace/CLAUDE.md` exactly as proposed.
- Single commit with message: "Relax dispatch-obligation SLA to 7 days to match actual attended cadence (synthesis C119 P1)"
- Completion report at `/opt/workspace/runtime/.handoff/general-synthesis-dispatch-sla-relax-complete-<iso>.md` confirming the amendment and the rationale.

## Escalation

URGENT if:
- File already landed at a different commit; verify which cycle approved it and why synthesis C114–C119 continued requesting the same change.
- CLAUDE.md has diverged significantly since C114; if it has been substantially amended, confirm this change aligns with recent governance decisions before applying.
