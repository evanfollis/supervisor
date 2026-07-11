---
from: synthesis-translator
to: general
date: 2026-05-18T15:34:15Z
priority: high
task_id: synthesis-reflection-verify-files
source_synthesis: /opt/workspace/runtime/.meta/cross-cutting-2026-05-18T15-27-09Z.md
source_proposal: Proposal 3 — Reflection must verify file state, not trust event claims
---

# Reflection must verify file state, not trust event claims

**Type:** Shared primitive change — `supervisor/scripts/lib/reflect-prompt.md` (or reflect-supervisor-prompt.md)

Add to the reflection prompt instructions:

> **Verification rule:** When reporting the state of a file (frontmatter dates, content, counts), you MUST read the file directly. Do not cite tick events, session notes, or prior reflections as evidence of current file state. Event claims describe what a job intended to do; file reads describe what actually happened. If they conflict, the file read wins and the conflict is itself a finding.

**Blast radius:** All reflection jobs (automatic). No code change — prompt amendment only.
**Cycles open:** 1.

## Rationale from synthesis

The supervisor reflection at 14:26Z reported that active-issues.md frontmatter was bumped from 2026-05-14 to 2026-05-18, citing events. Direct verification revealed the frontmatter is still 2026-05-14 and the tick branch was never merged. The reflection inherited false state from event citations. This is diagnostic-chain contamination: the surface supposed to catch state divergence has itself become unreliable. The fix is a single verification rule in the reflection prompt.

## Verification before action (required)

- Check if the reflection prompt files already contain a similar verification rule.
- Search the prompt directory for existing "verify file directly" or "trust file over event" language.
- If the rule already exists (in any form), document it and report "already present" rather than duplicating.

## Acceptance criteria

- The verification rule is added to the reflection prompt (likely `supervisor/scripts/lib/reflect-prompt.md` or a supervisor-specific variant).
- The rule is clear and mandatory (use MUST language, not MAY or SHOULD).
- On the next reflection cycle, spot-check the reflection output to verify it now cites file reads rather than event claims.
- Completion report at `runtime/.handoff/general-supervisor-synthesis-reflection-verify-files-complete-<iso>.md`.

## Escalation

URGENT if:
- The reflection system has multiple prompt files and the rule must be added to all of them. Verify which prompt files are live before applying.
- Adding this rule conflicts with existing event-sourcing semantics in the reflection design. If events are the intended truth source for some fields, that's a design conflict requiring principal review, not a routine prompt amendment.
