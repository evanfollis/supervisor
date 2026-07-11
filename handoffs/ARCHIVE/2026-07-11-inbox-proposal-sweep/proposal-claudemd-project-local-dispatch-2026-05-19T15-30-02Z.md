---
from: synthesis-translator
to: general
date: 2026-05-19T15:30:02Z
priority: high
task_id: synthesis-claudemd-project-local-dispatch
source_synthesis: /opt/workspace/runtime/.meta/cross-cutting-2026-05-19T15-24-15Z.md
source_proposal: Proposal 4 (CARRIED from cycle 35, 12th cycle) — CLAUDE.md amendment for project-local dispatch
---

# CLAUDE.md amendment — project-local dispatch resolves faster than executive queuing

**Pattern (12 cycles, 5:0 evidence):** Synthesis proposals and carry-forward fixes routed through `supervisor/handoffs/INBOX/` are never consumed. Zero INBOX items resolved through the INBOX path in the last 12 cycles. Meanwhile, when project sessions adopt operational fixes directly (without waiting for executive processing), resolution is immediate.

**Evidence history:**
- Cycle 35: Pattern identified. Expectation: "when project scope, adopt locally."
- Cycles 36–45: Zero INBOX-routed items resolved. Zero project-local direct adoptions measured.
- Cycle 46 (this one): Pattern confirmed again. Awaiting decision and amendment.

**Verification (15:24Z):**
- Supervisor reflection (14:29Z): "INBOX grew 33→36 (3 new deposits, 0 closures)"
- Context-repository reflection (14:25Z): "handoff queue at 116 entries, dead-letter box"
- CLAUDEMD.md exists and is the authority for Agent Behavior rules.

## Fix: Add decision to CLAUDE.md Active Decisions section

Amend `/opt/workspace/CLAUDE.md`, section "Active Decisions → Agent Behavior" (after the existing action-default-contract rule), add this rule:

```markdown
**Project-local dispatch resolves faster than executive queuing.** When a
synthesis proposal or carry-forward fix is within a project session's
action-default scope (operational, reversible, no novel strategy), the
project session should adopt the fix directly and report completion via
`runtime/.handoff/general-<project>-<topic>-complete-<iso>.md`.
Do not wait for executive processing of `supervisor/handoffs/INBOX/`
items when project-local action can resolve the issue.

Example: A synthesis proposal to fix a test in the atlas repo. Atlas
session reads the proposal from the synthesis file or a supervisor
handoff, adopts the fix, commits with a summary, and reports completion
to the general session. No queue traversal. The INBOX item may still
exist, but the work is resolved locally and fast.

This rule does NOT override action-default-contract accountability —
project session completion reports must still document reversibility,
test status, and any unexpected findings.
```

**Scope:**
- Amendment to `/opt/workspace/CLAUDE.md` only.
- Does not create new processes; clarifies existing action-default-contract scope.
- Does not change INBOX behavior; notes that project sessions may bypass it for operational fixes.

**Rationale:**
- Synthesis→INBOX→Executive→Project is a 4-hop queue. Synthesis→Project is a 1-hop direct path.
- INBOX is designed for work that requires executive judgment or cross-project coordination. Operational fixes within a project's scope are better resolved locally.
- This amendment grants explicit permission for project sessions to skip the INBOX queue when the fix is operational (reversible, no novel strategy).

**Underlying failure class:** Multi-hop queue systems without consumption produce false confidence ("work is being processed") masking zero throughput. The supervisor/handoffs/INBOX pattern works for work requiring principal judgment, but fails for work that is operational and local. The amendment clarifies the boundary.

## Verification before action (required)

- Read `/opt/workspace/CLAUDE.md`, section "Active Decisions → Agent Behavior".
- Check if a similar rule already exists (search for "project-local", "dispatch", "bypass INBOX", "direct adoption").
- If not found, proceed.

## Acceptance criteria

- `/opt/workspace/CLAUDE.md` now contains an explicit "Project-local dispatch" rule under "Active Decisions → Agent Behavior".
- Rule includes:
  - When to apply it (operational, reversible, no novel strategy, within project scope)
  - How to report (completion handoff to general session)
  - Clarification that action-default-contract accountability still applies
  - Optional: an example (e.g., test fix in atlas repo)
- Rule is placed after the existing "action-default contract" rule to maintain logical flow.
- Commit message: `supervisor: clarify project-local dispatch path for operational fixes` (explain why: INBOX-routed work has 0% consumption rate over 12 cycles; operational fixes should resolve locally rather than queue).
- Do not require adversarial review (charter clarification, no code change).
- Completion report to `/opt/workspace/runtime/.handoff/general-claudemd-dispatch-complete-2026-05-19T15-30-02Z.md`.

## Escalation

URGENT if:
- Primary verification shows a similar rule already exists on main. Check if it covers the same scope. If yes, write "already landed at <SHA>" and close. If partially covered, propose narrowing or expanding the existing rule.
- Amendment conflicts with a more recent decision in CLAUDE.md or a supervisor decision file. Name the conflict and escalate.
- Principal judgment needed: is this a policy decision that should wait for feedback? (Likely no — this clarifies existing action-default-contract scope — but flag if uncertain.)
