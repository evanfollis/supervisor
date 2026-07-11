---
from: synthesis-translator
to: supervisor
date: 2026-05-18T03:30:49Z
priority: high
task_id: synthesis-claude-md-project-local-dispatch-9th-cycle
source_synthesis: /opt/workspace/runtime/.meta/cross-cutting-2026-05-18T03-26-35Z.md
source_proposal: Proposal 5 — CLAUDE.md amendment — project-local dispatch
---

# CLAUDE.md amendment — project-local dispatch

**Type:** Charter amendment — `/opt/workspace/CLAUDE.md`

**Evidence ratio:** 5:0. No INBOX-routed item has resolved in the observation period. Evidence from 9 cycles of synthesis observations: project-local action (a project session adopting and fixing a synthesis proposal without waiting for executive INBOX processing) has succeeded 5 times with 0 failures.

**Proposal (unchanged from cycle 42, exact text):**

Insert the following amendment into `/opt/workspace/CLAUDE.md` under the **Active Decisions** section, **Agent Behavior** subsection, as a new paragraph immediately after the "Action-default contract (ADR-0020)" bullet:

```markdown
- **Project-local dispatch resolves faster than executive queuing.** When a
synthesis proposal or carry-forward fix is within a project session's
action-default scope (operational, reversible, no novel strategy), the project
session should adopt the fix directly and report completion via
`runtime/.handoff/`. Do not wait for executive processing of
`supervisor/handoffs/INBOX/` items when project-local action can resolve the
issue.
```

**Rationale:**

The current charter (ADR-0020) establishes action-default: project sessions default to taking reversible action rather than asking permission. However, when a synthesis proposal arrives at INBOX and names a specific project, the current pattern is:

1. Proposal lands in INBOX
2. Executive reads INBOX (1–3 cycles later)
3. Executive dispatches handoff to project (if applicable)
4. Project session reads and executes handoff

This adds 2–3 cycles of latency. Actual evidence shows project sessions can skip step 2 and 3 when:

- The proposal is clearly reversible (code/config change, not strategy)
- The project session is the natural owner of the target file/system
- The fix is within the action-default scope already granted in ADR-0020

This amendment codifies that pattern. It does not weaken supervision — the completion report to `runtime/.handoff/general-...-complete` still documents what the project did. It just removes the queue hop.

**Blast radius:** All project sessions (automatic, policy codification only).

**Cycles open:** 9. Validation ratio: 5 validating instances observed, 0 failures.

## Verification before action (required)

- Check `/opt/workspace/CLAUDE.md` section "### Agent Behavior" — verify the amendment text is not already present
- `git log --oneline -20 CLAUDE.md` — confirm this amendment has not landed via another path
- Look for the exact location: after "Action-default contract (ADR-0020)" bullet within Agent Behavior

## Acceptance criteria

- Amendment text inserted into CLAUDE.md at the specified location (after ADR-0020 in Agent Behavior)
- Text is verbatim from proposal above (no paraphrasing)
- Commit message explains the 9-cycle carry-forward and the 5:0 validation ratio
- No other changes to CLAUDE.md in this commit
- Use `git diff CLAUDE.md` to verify the placement is correct

## Escalation

URGENT if:
- A recent executive decision or ADR contradicts the premise of this amendment (e.g. a new rule requiring all synthesis proposals to queue through INBOX) — if so, the amendment conflicts and should not land until the conflict is resolved
