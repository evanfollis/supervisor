---
from: synthesis-translator
to: executive
date: 2026-06-29T15:30:33Z
priority: high
task_id: synthesis-p1-dispatch-sla-24h-to-7d
source_synthesis: /opt/workspace/runtime/.meta/cross-cutting-2026-06-29T15-27-11Z.md
source_proposal: P1 (AMENDMENT) — Relax dispatch obligation to match attended cadence
---

# P1 (AMENDMENT): Relax dispatch obligation to match attended cadence

**Type:** CLAUDE.md amendment — "Automated Self-Reflection Loop" section, dispatch obligation paragraph.

**Current text:**
> Synthesis proposals sitting >24h without dispatched action or recorded deferral escalate as FR-class structural issues.

**Proposed replacement:**
> Synthesis proposals sitting >7 days without dispatched action or recorded deferral escalate as FR-class structural issues. The 7-day window reflects the actual attended cadence of this workspace; a tighter SLA produces breach noise rather than useful pressure when sessions are less frequent.

**Rationale:** The 24h SLA has breached 3 consecutive times and will continue breaching indefinitely at current attendance patterns. The breach record is noise, not signal. A 7-day SLA would fire only when something is genuinely stale, and the synthesis-translator INBOX growth rate would drop to ~1-2 items/week instead of ~10/day.

**Blast radius:** Supervisor only (dispatch obligation enforcement). Automatic once CLAUDE.md is amended.

## Verification before action (required)

- Run `git log --oneline -20` on `/opt/workspace/` and check if this amendment has already landed via another path.
- Read `/opt/workspace/CLAUDE.md` line ~194. Check if the text already says "7 days" or "7d".
- If either is true, write a completion report stating "already landed" rather than re-applying.

## Acceptance criteria

- The dispatch obligation text in `/opt/workspace/CLAUDE.md` (Automated Self-Reflection Loop section) is amended to say "7 days" instead of "24h".
- The change is committed with a clear message explaining the synthesis source and the rationale.
- Completion report at `runtime/.handoff/general-supervisor-synthesis-p1-complete-<iso>.md` pointing back to this handoff and the source synthesis.

## Escalation

URGENT if:
- The amendment conflicts with a more recent decision in `supervisor/decisions/`. Do not force-apply; escalate with the conflict named.
- The amendment requires principal input to override (principal has stated otherwise in recent JSONL or decisions/). Surface the specific statement.
