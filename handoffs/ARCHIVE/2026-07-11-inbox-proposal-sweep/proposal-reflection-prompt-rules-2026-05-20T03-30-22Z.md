---
from: synthesis-translator
to: general
date: 2026-05-20T03:30:22Z
priority: medium
task_id: synthesis-reflection-prompt-rules
source_synthesis: /opt/workspace/runtime/.meta/cross-cutting-2026-05-20T03-25-45Z.md
source_proposal: "Proposal 3 (MEDIUM — 4th/2nd cycle): Verification rules in reflection prompts"
---

# Verification rules in reflection prompts

## Context

The reflection system sometimes emits events that later verify as incorrect (e.g., claiming "FR-0042 filed on main first time" when the file doesn't exist on main). The system benefits from explicit verification rules in the reflection prompts that guide the reflection sessions to verify claims against primary sources before accepting event claims.

## The Fix

Two reflection prompt amendments from cycle 46 (both sketched but not yet landed):

### Rule 1: File-state verification (4th cycle open)
**Target**: `supervisor/scripts/lib/reflect-prompt.md` and `reflect-supervisor-prompt.md`
**Guidance**: Before accepting a tick or event claim about a file, project, or state ("FR-0042 was filed", "X was committed", "service is live"), reflect the actual file/repo state:
- `cat` the file to confirm it exists
- `git log` to confirm the commit exists
- `git status` to confirm the state reported
- If the claim and the state diverge, record the divergence as a friction observation, not as verified fact

Insert into the "Principle adherence" section:

```markdown
- **Diagnostic sources verified against primary artifacts.** Before accepting a claim from a tick event, session event, or prior reflection, verify the underlying artifact: `git log` for commit claims, `cat` for file claims, `git status` for state claims. If a claim and the artifact diverge, the artifact wins and the divergence is a friction signal (false event, stale reflection, tick-isolation bug). Never report artifact state based on what a prior artifact said it was.
```

### Rule 2: Diagnostic-target divergence (2nd cycle open)
**Target**: Same files as Rule 1
**Guidance**: Reflect-supervisor should read actual supervisor repo state (`git log`, `git status`, file contents) and compare against what the tick events claim. If divergence exists, the repo state is ground truth and the event is questionable.

Insert into the "Artifacts to read" section (after reading git log/status, add):

```markdown
- **Verify all tick-event claims against file/git state.** If a session event claims "X was filed" but no file matches, record the divergence. If a prior reflection claimed a decision was recorded but no decision file exists, record that. Event-stream correctness is a property that needs explicit verification, not a property you should accept on faith.
```

## Blast Radius

- Reflection prompts only (no code logic changes)
- Affects all reflection jobs (automatic, next 12h cycle)
- Improves diagnostic accuracy across supervisor and all projects

## Cycles open

- Rule 1: 4 cycles
- Rule 2: 2 cycles

## Verification before action (required)

- Read `supervisor/scripts/lib/reflect-prompt.md` and `reflect-supervisor-prompt.md` to see current state
- Confirm these files exist and are accessible
- Check if rules are already present (search for "primary artifacts" and "tick-event claims") — if found, mark as already landed
- If files don't exist, escalate with the missing path

## Acceptance criteria

- Both rules are added to the relevant reflection prompts
- Rules guide reflection sessions to verify claims against primary sources before accepting them
- Commit message explains the verification improvements
- Change tested by running a reflection cycle (or at least code-reviewed for clarity)
- Completion report at `runtime/.handoff/general-supervisor-synthesis-reflection-rules-complete-<iso>.md`

## Escalation

URGENT if:
- The rules are already present (landed by another path between synthesis and now)
- Adding rules would require changing the reflection prompt structure in a way that conflicts with other cycle 47 changes
