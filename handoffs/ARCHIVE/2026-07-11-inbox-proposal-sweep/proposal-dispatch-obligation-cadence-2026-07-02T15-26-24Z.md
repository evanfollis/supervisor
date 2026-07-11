---
from: synthesis-translator
to: general
date: 2026-07-02T15:26:24Z
priority: high
task_id: synthesis-dispatch-obligation-cadence
source_synthesis: /opt/workspace/runtime/.meta/cross-cutting-2026-07-02T15-23-04Z.md
source_proposal: P1 (CARRY — C114, 7th cycle)
---

# P1: Relax dispatch obligation to match attended cadence

**Type:** CLAUDE.md amendment — "Automated Self-Reflection Loop" section.

**Context:** The current 24h dispatch obligation produces breach noise rather than useful pressure in a workspace with 7-day attended cadence. The synthesis has carried this proposal through 7 cycles (C114 → C120) and notes 9 consecutive dispatch obligation breaches (C110-C119). The first appears at ~113h past SLA.

**Current text in `/opt/workspace/CLAUDE.md` (line 194):**
```
- **Dispatch obligation.** When a synthesis proposal lands in `runtime/.meta/cross-cutting-*.md`, the executive must dispatch a delegated project session within 24h — via `runtime/.handoff/<project>-*.md` handoff — or record an explicit deferral reason in `supervisor/decisions/` or `runtime/.meta/`. Synthesis proposals sitting >24h without dispatched action or recorded deferral escalate as FR-class structural issues. The reflection/synthesis loop is a work queue, not a diagnostic archive; treating proposals as read-and-file produces the "80h perfect-diagnosis-zero-execution" failure class the loop was designed to prevent.
```

**Proposed replacement:**
```
- **Dispatch obligation.** When a synthesis proposal lands in `runtime/.meta/cross-cutting-*.md`, the executive must dispatch a delegated project session within 7 days — via `runtime/.handoff/<project>-*.md` handoff — or record an explicit deferral reason in `supervisor/decisions/` or `runtime/.meta/`. Synthesis proposals sitting >7 days without dispatched action or recorded deferral escalate as FR-class structural issues. The 7-day window reflects the actual attended cadence of this workspace; a tighter SLA produces breach noise rather than useful pressure when sessions are less frequent. The reflection/synthesis loop is a work queue, not a diagnostic archive; treating proposals as read-and-file produces the "80h perfect-diagnosis-zero-execution" failure class the loop was designed to prevent.
```

**Rationale:** C114 P1 analysis: "Unfunded mandate — dispatch obligation exceeds attended cadence. Counter: 9th consecutive dispatch breach (C110-C119)... Atlas handoff now ~113h past SLA — record breach continues to extend." This amendment aligns the formal SLA with the actual cadence to restore useful signal vs. noise.

**Blast radius:** Supervisor only. No code changes required once CLAUDE.md is amended.

## Verification before action (required)

- Confirm the current text at `/opt/workspace/CLAUDE.md:194` matches the "Current text" section above.
- If already amended, write a completion report stating "already landed" with the commit SHA.

## Acceptance criteria

- The 24h language is replaced with 7-day language in both sentences.
- One commit with clear message: "amend dispatch obligation SLA to 7 days per C120 P1"
- No other changes to the section.
- Completion report filed pointing back to this handoff.

## Escalation

URGENT if:
- The amendment has already landed via another path (check `git log --oneline -20 -- CLAUDE.md`).
- The principal has overridden this threshold in recent JSONL (check last 7 days of `/root/.claude/projects/-opt-workspace/*.jsonl`).
