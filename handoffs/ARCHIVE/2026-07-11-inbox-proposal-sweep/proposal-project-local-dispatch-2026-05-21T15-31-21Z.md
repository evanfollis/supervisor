---
from: synthesis-translator
to: general
date: 2026-05-21T15:31:21Z
priority: medium
task_id: synthesis-project-local-dispatch
source_synthesis: /opt/workspace/runtime/.meta/cross-cutting-2026-05-21T15-24-47Z.md
source_proposal: "Proposal 4 (MEDIUM — 16th cycle): CLAUDE.md amendment — project-local dispatch"
---

# CLAUDE.md amendment — project-local dispatch (NEEDS CLARIFICATION)

**Type:** CLAUDE.md amendment (charter-level governance).

**Status in synthesis:** "Unresolved" (line 116).

**Blast radius:** All project sessions (automatic once clarified and landed).

**Current state:** Proposal 4 has been carried for 16 cycles without clear definition of what "project-local dispatch" means.

## Issue

The synthesis identifies this as a distinct proposal but does not specify:
- What the current dispatch model is (centralized? mixed?)
- What the target "project-local" model should be
- Which behaviors change and which stay the same
- Whether this is about handoff routing, decision authority, or execution scope

Without this clarity, the proposal cannot be executed as stated.

## Before action

**The principal must clarify what "project-local dispatch" means in this context.**

Possible interpretations (not exhaustive):
1. **Dispatch authority**: Project sessions handle their own dispatch of work, rather than routing through the supervisor
2. **Handoff routing**: Project sessions write handoffs to themselves rather than routing through the executive
3. **Escalation thresholds**: Projects have local SLAs for when to escalate to the supervisor, separate from workspace-wide SLAs
4. **Autonomy scope**: Projects are authorized to dispatch work to other projects without supervisor mediation

## Verification before action (required)

- ⚠️  Proposal is underspecified. No amendment text is provided.
- ⚠️  Synthesis carries the proposal but marks it "Unresolved" without clarification.
- ⚠️  This proposal has been open for 16 cycles without forward progress due to lack of definition.
- Do not attempt to implement without principal input.

## Acceptance criteria (pending clarification)

Once the principal clarifies what "project-local dispatch" means:
1. Propose specific amendment text to `/opt/workspace/supervisor/CLAUDE.md`
2. Include: the target state, which behaviors change, why the change improves dispatch
3. Route to adversarial review before committing
4. Update `CLAUDE.md` with the approved amendment
5. Emit event: `decision_recorded` pointing to the ADR or amended section

## Escalation (REQUIRED — principal input needed)

**This proposal cannot move forward without principal clarification.** 

**Question for the principal:** What does "project-local dispatch" mean? What specific governance change should this proposal make to `/opt/workspace/supervisor/CLAUDE.md`?

Hold this handoff open until clarified. Once clarified, a concrete amendment can be drafted and executed.
