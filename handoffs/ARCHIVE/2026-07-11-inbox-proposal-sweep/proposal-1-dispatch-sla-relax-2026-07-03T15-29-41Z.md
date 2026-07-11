---
from: synthesis-translator
to: general
date: 2026-07-03T15:29:41Z
priority: high
task_id: synthesis-dispatch-sla-relax
source_synthesis: /opt/workspace/runtime/.meta/cross-cutting-2026-07-03T15-24-18Z.md
source_proposal: P1 (CARRY — C114, 9th cycle): Relax dispatch obligation to match attended cadence
---

# P1: Relax dispatch obligation SLA to match attended cadence

**Type:** CLAUDE.md amendment — "Automated Self-Reflection Loop" section.

**Current text (line 194 of `/opt/workspace/CLAUDE.md`):**
```
- **Dispatch obligation.** When a synthesis proposal lands in `runtime/.meta/cross-cutting-*.md`, the executive must dispatch a delegated project session within 24h — via `runtime/.handoff/<project>-*.md` handoff — or record an explicit deferral reason in `supervisor/decisions/` or `runtime/.meta/`. Synthesis proposals sitting >24h without dispatched action or recorded deferral escalate as FR-class structural issues. The reflection/synthesis loop is a work queue, not a diagnostic archive; treating proposals as read-and-file produces the "80h perfect-diagnosis-zero-execution" failure class the loop was designed to prevent.
```

**Proposed replacement:**
```
- **Dispatch obligation.** When a synthesis proposal lands in `runtime/.meta/cross-cutting-*.md`, the executive must dispatch a delegated project session within 7 days — via `runtime/.handoff/<project>-*.md` handoff — or record an explicit deferral reason in `supervisor/decisions/` or `runtime/.meta/`. Synthesis proposals sitting >7 days without dispatched action or recorded deferral escalate as FR-class structural issues. The 7-day window reflects the actual attended cadence of this workspace; a tighter SLA produces breach noise rather than useful pressure when sessions are less frequent. The reflection/synthesis loop is a work queue, not a diagnostic archive; treating proposals as read-and-file produces the "80h perfect-diagnosis-zero-execution" failure class the loop was designed to prevent.
```

## Rationale (from C122 synthesis)

The 24h dispatch SLA was designed for a workspace with daily attended sessions. The current attended cadence is approximately once per 4–7 days. The 24h SLA correctly fires a breach counter every 12h reflection cycle, but this measures a miscalibrated SLA, not actual dispatch behavior. Relaxing to 7 days aligns the SLA with observed cadence and eliminates false-positive breach noise.

This is the 22nd consecutive synthesis request for this same fix (since C114).

## Verification before action (required)

- Run `git log --oneline -20` on `/opt/workspace/` to check if this amendment has already landed.
- Read line 194 of `/opt/workspace/CLAUDE.md` — verify the current text still says "24h" not "7 days".
- If amendment is already landed, write a completion report stating "already landed at commit <SHA>".

## Acceptance criteria

- Line 194 of `/opt/workspace/CLAUDE.md` is amended: "24h" → "7 days" + supporting context added.
- Change committed with message: `Relax dispatch obligation SLA to 7 days to match actual attended cadence`
- Commit includes the rationale explaining why the prior SLA was misaligned.
- No adversarial review needed (configuration change, not design).
- Completion report written to `runtime/.handoff/general-dispatch-sla-complete-<iso>.md`.

## Escalation

None anticipated. This is a mechanical configuration alignment. No external dependencies.
