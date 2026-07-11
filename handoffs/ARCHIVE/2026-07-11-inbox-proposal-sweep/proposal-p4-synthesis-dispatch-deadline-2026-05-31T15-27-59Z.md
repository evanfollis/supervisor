---
from: synthesis-translator
to: general
date: 2026-05-31T15:27:59Z
priority: high
task_id: synthesis-p4-synthesis-dispatch-deadline
source_synthesis: /opt/workspace/runtime/.meta/cross-cutting-2026-05-31T15-23-50Z.md
source_proposal: P4 — Synthesis dispatch deadline enforcement
---

# P4 — Synthesis dispatch deadline enforcement

**Type**: CLAUDE.md amendment

**Proposed text** (addition to "Automated Self-Reflection Loop" section in `/opt/workspace/CLAUDE.md`):

```markdown
### Synthesis dispatch deadline advisory during dormant periods

When the workspace has zero attended sessions for 3+ consecutive cycles and no 
project activity outside the supervisor, the 24h dispatch obligation is suspended. 
The synthesis file remains the escalation surface. The obligation reactivates when 
an attended session opens or project activity resumes.
```

**Rationale**: The dispatch rule assumes an executive session exists to consume dispatches. During dormant periods, the rule produces breach counters that accumulate without actionable consequence. Making it advisory during dormancy eliminates a false-positive escalation signal without weakening the rule when it matters (when someone is actually available to act on it).

**Blast radius**: Workspace-wide policy. Opt-in (requires CLAUDE.md edit).

## Verification before action (required)

- Run `git log --oneline -5` on `supervisor/`. Check if a similar amendment has already landed.
- Search `/opt/workspace/CLAUDE.md` for "Synthesis dispatch deadline". Verify the proposed text is NOT yet present.
- If either check shows this is already applied, write a completion report stating "already landed" rather than re-applying.

## Acceptance criteria

- The proposed text (or equivalent with the same meaning) is now present in the "Automated Self-Reflection Loop" section of `/opt/workspace/CLAUDE.md`.
- Change committed with clear message explaining the synthesis source and the rationale (9+ dispatch deadline breaches during dormancy).
- Completion report at `runtime/.handoff/general-supervisor-synthesis-p4-complete-<iso>.md` pointing back to this handoff.

## Escalation

URGENT if:
- Primary verification reveals this amendment has already landed. Write a brief completion report saying "already landed" and close.
- The amendment conflicts with a recent ADR or charter principle. Escalate with the conflict named and escalate to the principal for final judgment.
