---
from: synthesis-translator
to: general
date: 2026-05-26T03:27:59Z
priority: high
task_id: synthesis-synthesis-aging-gate
source_synthesis: /opt/workspace/runtime/.meta/cross-cutting-2026-05-26T03-23-30Z.md
source_proposal: Proposal 3 — Synthesis proposal aging gate
---

# Proposal 3: Synthesis proposal aging gate

**Type:** CLAUDE.md amendment — new subsection under "Automated Self-Reflection Loop."

**What:** C58 Proposal 1, carried forward with classification. If a synthesis proposal has been open >2 cycles, the next synthesis must classify the blocker (attended-session-blocked, Tier-B-auto-blocked, principal-decision-blocked, or withdrawn). Proposals in the first two categories for >4 cycles escalate to URGENT. Proposals in the third category move to "Pending principal" and are suppressed from further carry-forward.

```markdown
### Synthesis proposal aging gate
A synthesis proposal open for >2 cycles without a corresponding code
change, decision verdict, or explicit deferral in `decisions/` must be
classified by the next synthesis into one of:
- **Attended-session-blocked**: requires human presence.
- **Tier-B-auto-blocked**: tick has the information but not the authority.
- **Principal-decision-blocked**: requires input only the principal can give.
- **Withdrawn**: the proposal was wrong or superseded; remove.

Proposals in the first two categories for >4 cycles escalate to an
URGENT handoff (subject to INBOX saturation rules). Proposals in the
third category are moved to "Pending principal" in active-issues.md and
suppressed from further synthesis carry-forward.
```

**Why:** C58 produced 4 proposals, 0 landed. C57 produced 4, 0 landed. The synthesis loop has a 1/8 (~12.5%) proposal-to-landing rate over the last 2 full cycles. Without blocker classification, it is impossible to distinguish "wrong proposal" from "blocked execution path." The gate converts carry-forwards from advisory to diagnostic.

**Blast radius:** All synthesis cycles (automatic). Changes synthesis behavior only.

## Verification before action (required)

- Run `grep -c "Synthesis proposal aging gate" /opt/workspace/CLAUDE.md` to verify this rule is not already present.
- Read the "Automated Self-Reflection Loop" section in `/opt/workspace/CLAUDE.md` to confirm placement target and related sections.

## Acceptance criteria

- New subsection "### Synthesis proposal aging gate" is added to the "Automated Self-Reflection Loop" section in `/opt/workspace/CLAUDE.md`.
- The exact text above (or equivalent formulation) is added to the file, with all four blocker categories and escalation thresholds preserved.
- Change committed with message: "Add synthesis proposal aging gate (C59 P3)"
- Completion report at `/opt/workspace/runtime/.handoff/general-synthesis-synthesis-aging-gate-complete-<iso>.md` pointing to this handoff and source synthesis.

## Escalation

URGENT if:
- The rule is already present in `/opt/workspace/CLAUDE.md` (primary-verify via grep). Write "already landed" completion report instead.
- The proposed rule conflicts with existing synthesis behavior in `/opt/workspace/supervisor/scripts/lib/synthesize.sh` or related prompts. Surface the conflict.
- The proposed rule conflicts with a more recent decision. Surface the conflict.
