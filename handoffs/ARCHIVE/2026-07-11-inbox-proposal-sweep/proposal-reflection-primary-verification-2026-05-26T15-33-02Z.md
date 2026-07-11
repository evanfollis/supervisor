---
from: synthesis-translator
to: general
date: 2026-05-26T15:33:02Z
priority: high
task_id: synthesis-proposal-3-reflection-verification
source_synthesis: /opt/workspace/runtime/.meta/cross-cutting-2026-05-26T15-27-05Z.md
source_proposal: Proposal 3 — Reflection sessions must verify secondary-source claims before escalating
---

# Reflection sessions must verify secondary-source claims before escalating

## Proposal body (from synthesis)

**Type:** CLAUDE.md amendment — new subsection under "Automated Self-Reflection Loop."

**What:** Before a reflection session escalates a finding based on a secondary source (active-issues claim, milestone table, event log entry), it must cross-check the primary source. If the primary source contradicts the secondary source, the reflection should flag the drift rather than escalating the stale claim.

```markdown
### Reflection primary-verification discipline
Before escalating a finding based on a secondary source
(active-issues.md, milestone tables, event logs), reflection sessions
must cross-check the primary source (code, verified-state.md, filesystem,
git log). If the primary source contradicts the secondary source, the
reflection should flag the drift as its finding rather than escalating
the stale secondary claim.
```

**Why:** Pattern 1 documents three instances this window where secondary sources produced false or stale claims. The primary-verification gate in the charter covers the executive→principal channel. This extends the same discipline to reflection→synthesis and tick→active-issues channels. Would have prevented 4 cycles of recommerce false alarm and caught the kernel version drift earlier.

**Blast radius:** All reflected projects (automatic). Changes reflection behavior only.

## Verification before action (required)

- Check `/opt/workspace/CLAUDE.md` under the "Automated Self-Reflection Loop" section for "Reflection primary-verification discipline" or similar subsection.
- If found and it matches the proposal content above, this is already landed; report "already landed" and close.
- If not found, proceed with the amendment.
- Verify the location: should be a new subsection **within** "### Automated Self-Reflection Loop", not at the top level.

## Acceptance criteria

- Add the new subsection "Reflection primary-verification discipline" as part of the "Automated Self-Reflection Loop" section in `/opt/workspace/CLAUDE.md`.
- The rule requires reflection sessions to cross-check secondary sources against primary sources before escalating.
- Name the primary sources (code, `verified-state.md`, filesystem, git log) and secondary sources (active-issues, milestone tables, event logs).
- Clearly state that if primary and secondary sources diverge, the reflection should flag the drift rather than escalate the stale claim.
- Commit with message: "Add reflection primary-verification discipline to prevent stale secondary-source escalations (Pattern 1, Cycle 60)"
- Reference the synthesis source and the three instances it prevented.
- No adversarial review required (reflection instruction enhancement, addresses known failure class).
- Completion report to `/opt/workspace/runtime/.handoff/general-proposal-3-synthesis-reflection-verify-complete-2026-05-26T15-33-02Z.md`.

## Escalation

URGENT if:
- The "Automated Self-Reflection Loop" section structure has changed significantly and the placement of this subsection is ambiguous.
- Reflection sessions are already performing primary verification and the synthesis was unaware of it (check reflected project CURRENT_STATE.md files and prior reflection outputs).
