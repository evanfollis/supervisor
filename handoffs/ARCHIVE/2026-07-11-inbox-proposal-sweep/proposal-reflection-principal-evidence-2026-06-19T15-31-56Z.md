---
from: synthesis-translator
to: general
date: 2026-06-19T15:31:56Z
priority: medium
task_id: synthesis-reflection-principal-evidence
source_synthesis: /opt/workspace/runtime/.meta/cross-cutting-2026-06-19T15-27-31Z.md
source_proposal: 6. P-reflection-principal-evidence (refinement from C48)
---

# P-reflection-principal-evidence — Require positive evidence for "principal present" claim

**New refinement from C48 (supervisor-reflection-14:21Z). Prevents false positives.**

## Problem

C47 (supervisor reflection 02:22Z) falsely claimed "Principal is present" based on JSONL user-message count. Those messages were automated reflect.sh prompts, not human interaction. This produced a false positive that inflated the "attended session" count.

## Solution

Amend the reflection prompt to require at least **one of:**
1. Novel user directive (user typed a command that wasn't the scheduled reflect.sh prompt)
2. Diff outside automation scope (file changes that weren't from autocommit)
3. Confirmed tmux who/w output showing human session activity

This prevents claims of human presence based solely on automated prompts.

## Blast radius

All reflected projects. Opt-in (prompt text change). Improves accuracy of the "principal present" signal in reflections.

## Verification before action (required)

- Read the reflection prompt in `supervisor/scripts/lib/reflect.sh`. Check if positive-evidence rules are already documented.
- Check the current prompt template for "principal present" condition.
- If already in place, write a completion report saying "already landed in reflection prompt" and close.

## Acceptance criteria

- Reflection prompt amended to specify the three positive-evidence conditions above
- Change committed with message explaining the synthesis source and the C47 false-positive incident
- Completion report at `runtime/.handoff/general-supervisor-synthesis-reflection-principal-evidence-complete-<iso>.md` pointing back to this handoff and the source synthesis

## Why this matters

The "principal present" signal cascades into carry-forward tracking and dispatch urgency. False positives degrade the accuracy of the entire workspace-state model. This is a meta-accuracy improvement to the reflection loop.

## Escalation

URGENT if:
- The positive-evidence rules have already landed by another path.
- The reflection prompt architecture has fundamentally changed since this proposal was written.
