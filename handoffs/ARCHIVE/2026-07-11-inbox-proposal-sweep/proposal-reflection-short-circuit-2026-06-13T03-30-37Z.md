---
from: synthesis-translator
to: general
date: 2026-06-13T03:30:37Z
priority: medium
task_id: synthesis-reflection-short-circuit
source_synthesis: /opt/workspace/runtime/.meta/cross-cutting-2026-06-13T03-26-25Z.md
source_proposal: Proposal 3 — P-reflection-short-circuit
---

# P-reflection-short-circuit — Formalize reflection degradation rule

**Status:** Carried from C94 (2nd synthesis cycle). Context-repository has already self-degraded; this formalizes the pattern.
**Type:** Guidance amendment (low risk, opt-in).

## The problem

Reflection loops across multiple projects are in terminal degradation:

- **Context-repository:** Crossed its P3 threshold. Now writing single-paragraph reflections (first loop to voluntarily degrade).
- **Skillfoundry-harness:** "The reflection loop has fully exhausted its escalation vocabulary across all open items."
- **Command:** 12th consecutive quiet window, suppression fully engaged.
- **Atlas:** P2 at 6th carry-forward with synthesis URGENT not filed.

When every observation has been repeated 5+ cycles without response, the reflection loop rationally degrades into a timestamped confirmation that nothing changed. This conserves tokens and stops making noise about items no one is acting on.

**Current behavior:** Each loop invent its own threshold and degrade independently (context-repo already did this).

**Desired behavior:** Formalize the threshold and degradation rule so reflection loops don't have to rediscover it.

## What to fix

File: `supervisor/scripts/lib/reflect-prompt.md`

Add a new section after the existing "Short-circuit rule" (line ~26) with this guidance:

```markdown
## Status-update short-circuit rule

If ALL observations in your prior reflection are unchanged (same items, 
same status, no new findings), and this is the 4th+ consecutive cycle 
with no change, you MAY reduce your output to a single paragraph status update:

> **Short-circuit: cycle N.** M observations unchanged since [prior 
> reflection path]. Oldest unresolved: [item, age]. No new findings. 
> [Any NEW observation gets a full write-up here.]

Resume full analysis when any observation changes status or new findings emerge.
```

## Why this matters

- Context-repository has already self-degraded (evidence that the rule works).
- Formalizing it prevents 10+ lines of token waste per cycle when a reflection has nothing new.
- Allows reflection loops to signal "I've stopped because the diagnostics are exhausted" honestly instead of silently compacting their output.

## Verification before action (required)

- Read `supervisor/scripts/lib/reflect-prompt.md`. Check if a "status-update short-circuit" section already exists (not the same as the existing "Short-circuit rule" for no-activity).
- If the section exists and matches the proposal, write a completion report: "Already landed in file / verified."
- If the existing "Short-circuit rule" has been modified to match this proposal, write a completion report: "Landed as modified short-circuit rule."

## Acceptance criteria

- The new section is added to `reflect-prompt.md`.
- It appears after (not integrated into) the existing no-activity short-circuit rule.
- Guidance is permissive ("MAY", not "MUST").
- Change committed with clear message explaining the synthesis source.
- Completion report written to `runtime/.handoff/general-supervisor-synthesis-reflection-short-circuit-complete-<iso>.md`.

## Expected impact

- Cleaner reflection output when observations are stalled.
- Removes the need for individual projects to invent degradation rules.
- Honest signaling that a reflection loop has exhausted its diagnostic vocabulary (vs. silently compacting).
