---
from: synthesis-translator
to: general
date: 2026-05-25T15:29:36Z
priority: high
task_id: synthesis-aging-gate
source_synthesis: /opt/workspace/runtime/.meta/cross-cutting-2026-05-25T15-25-05Z.md
source_proposal: Proposal 1 (NEW — structural): Synthesis proposal aging gate
---

# Synthesis proposal aging gate

## Proposal body

**Type:** CLAUDE.md amendment — new subsection under "Automated Self-Reflection Loop."

**What:** If a synthesis proposal has been open for >2 cycles without landing, the next synthesis must classify the blocker:

```markdown
### Synthesis proposal aging gate
A synthesis proposal open for >2 cycles without a corresponding code
change, decision verdict, or explicit deferral in `decisions/` must be
classified by the next synthesis into one of:
- **Attended-session-blocked**: requires human presence; note when last
  attended session occurred.
- **Tier-B-auto-blocked**: tick has the information but not the authority.
- **Principal-decision-blocked**: requires input only the principal can give.
- **Withdrawn**: the proposal was wrong or superseded; remove from
  standing recommendations.

Proposals in the first two categories for >4 cycles escalate to an URGENT
handoff (subject to INBOX saturation rules). Proposals in the third
category are moved to "Pending principal" in active-issues.md and
suppressed from further synthesis carry-forward.
```

**Why:** C57 produced 4 proposals. None landed. C56 produced 3, one landed (~33%). The current synthesis loop treats un-landed proposals as carry-forwards without distinguishing *why* they didn't land. This makes it impossible to tell whether the proposal is wrong, the execution path is blocked, or the workspace simply isn't consuming synthesis output. Classifying the blocker converts the carry-forward from advisory to diagnostic.

**Blast radius:** All synthesis cycles (automatic). Changes synthesis behavior only; no project impact.

## Verification before action (required)

- Run `grep "Synthesis proposal aging gate" /opt/workspace/CLAUDE.md` — should return empty if not yet landed.
- Check line count of "Automated Self-Reflection Loop" section in CLAUDE.md — proposal adds ~13 lines.

## Acceptance criteria

- The `### Synthesis proposal aging gate` subsection is added to `/opt/workspace/CLAUDE.md` under the "Automated Self-Reflection Loop" section (located after the "Session-start context load" section and before "Active Decisions").
- Subsection includes all four blocker classifications and the escalation logic for proposals >4 cycles.
- Change committed with clear message referencing synthesis cycle 58.
- No adversarial review needed (documentation amendment, no structural code change).

## Escalation

URGENT if primary verification reveals the proposal text is already present in CLAUDE.md — mark as already-landed and close.

---

## Completion report template

After landing, write a completion report at:
`/opt/workspace/runtime/.handoff/general-synthesis-aging-gate-complete-<iso>.md`

Include:
- Commit SHA where the change landed
- Brief note: "Synthesis proposal aging gate landed in C58 proposal 1"
- Reference back to this handoff
