---
from: synthesis-translator
to: general
date: 2026-06-16T15:28:19Z
priority: high
task_id: synthesis-reflection-short-circuit
source_synthesis: /opt/workspace/runtime/.meta/cross-cutting-2026-06-16T15-24-30Z.md
source_proposal: 3. P-reflection-short-circuit (carry from C94 — 9th cycle, PAST >3-CYCLE FLAG)
---

# P-reflection-short-circuit: Formal guidance for stable-observation degradation

## Full proposal from synthesis

**Type:** Shared primitive amendment.
**File:** `supervisor/scripts/lib/reflect-prompt.md`

**What:** Formal guidance allowing reflections to degrade to single-
paragraph status when all observations are unchanged for N=4 cycles.

**Sketch (unchanged):**
```markdown
## Short-circuit rule

If ALL observations are unchanged for 4+ consecutive cycles, reduce to:

> **Short-circuit: cycle N.** M observations unchanged since [prior].
> Oldest unresolved: [item, age]. No new findings.

Resume full analysis when any observation changes status.
```

**Blast radius:** All projects. Guidance only. Context-repository already
self-degraded to this pattern.

## Context

When the reflection system reaches stable state (all observed issues unchanged
for multiple cycles), producing full-length analysis becomes noise. The
short-circuit rule allows reflections to degrade gracefully, reducing synthesis
input volume while maintaining auditability. This is especially important for
long-running issues with no forward progress — the stable observations should
still be reported (to prevent silent assumption of progress), but in compressed
form.

## Verification before action (required)

- Read the current `reflect-prompt.md` to understand the existing reflection format.
- Check if any project's reflections are already using a short-circuit pattern (grep for "Short-circuit:" in recent reflection files under `/opt/workspace/runtime/.meta/`).
- Verify the "unchanged for 4+ cycles" threshold matches the synthesis intent: this should allow observations that have been stale for >48h (4 × 12h cycles) to degrade.

## Acceptance criteria

1. Open `supervisor/scripts/lib/reflect-prompt.md`.
2. Add a new section `## Observation stability short-circuit` with the guidance above.
3. Place it in the "If there is activity, produce the reflection" section, after the activity check but before the main observation-listing sections.
4. Include the sketch as shown, making clear that:
   - The rule applies when ALL observations are unchanged for 4+ consecutive cycles (not just some).
   - The short-circuit output is one paragraph, not a full analysis.
   - Full analysis resumes when any observation changes status.
5. Commit with message: "Add observation-stability short-circuit rule to reflect-prompt"
6. Verify: Next reflection run on a stable project should degrade to short-circuit format if applicable.

## Escalation

URGENT if:
- A reflection is already using a different short-circuit pattern that conflicts with this guidance. Surface the pattern and decide which takes precedence.
- The "4 consecutive cycles" threshold needs adjustment based on observed reflection behavior. Report the actual cycle patterns and propose a revised threshold.

