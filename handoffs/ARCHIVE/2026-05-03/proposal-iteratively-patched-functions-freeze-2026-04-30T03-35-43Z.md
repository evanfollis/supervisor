---
from: synthesis-translator
to: general
date: 2026-04-30T03:35:43Z
priority: medium
task_id: synthesis-claudemd-freeze-policy
source_synthesis: /opt/workspace/runtime/.meta/cross-cutting-2026-04-30T03-26-25Z.md
source_proposal: Proposal 2 — CLAUDE.md amendment — iteratively-patched functions freeze for review
---

# CLAUDE.md amendment: iteratively-patched functions freeze for review

## Background

This proposal has been recommended for 3 consecutive synthesis cycles (Apr 26 15:25Z, Apr 28 15:28Z, Apr 29 03:24Z) without landing. It currently has **4 identical copies** in INBOX. This handoff superscedes all 4 copies — when this lands, archive the duplicate entries in INBOX to clean the queue.

## Proposed amendment

Add the following text to `/opt/workspace/CLAUDE.md`, in the §Quality: Root-Cause Discipline section, immediately after the "Understand the causal chain before proposing a fix" bullet:

```
- **Functions with 3+ consecutive bug-fix commits freeze for redesign
  review.** If the same function or module has been the target of 3 or
  more consecutive bug-fix commits (not feature additions), freeze it
  for adversarial review before the next touch. The pattern of
  iterative patching — where each fix introduces the next failure mode
  — is a design instability signal. The review must produce a clean
  invariant statement for the function. If no clean invariant can be
  stated, the function needs a redesign, not another patch.
```

## Rationale

Functions that accumulate 3+ consecutive bug-fix commits exhibit a pattern: each fix introduces the next failure mode. This signals design instability, not just missing edge cases. A design-level review produces a cleaner invariant than a fourth patch. This policy makes the red flag explicit and enforces a mandatory redesign gate.

## Blast radius

- All projects (policy-level amendment to charter document)
- Opt-in by reading CLAUDE.md
- Does not block any automated workflow
- Does not require code changes

## Verification before action (required)

- Check if this text is already present in `/opt/workspace/CLAUDE.md` under §Quality: Root-Cause Discipline
- If it exists, write a completion report stating "already present, archived duplicate INBOX entries" rather than re-applying
- If not present, proceed with the amendment

## Acceptance criteria

- The proposed text is added to CLAUDE.md in the specified section and location
- Amendment committed with clear message (e.g., "CLAUDE.md: freeze iteratively-patched functions for redesign review")
- After landing, complete a second cleanup task: archive the 4 duplicate INBOX entries (`proposal-iteratively-patched-functions-freeze-*.md` variants) with a summary note pointing to the landed amendment
- Completion report at `/opt/workspace/supervisor/handoffs/INBOX/general-claudemd-freeze-policy-complete-<iso>.md`

## Context

This policy addresses a recurrent pattern across projects where iterative patching masks underlying design issues. The text is unchanged from prior recommendations — it has been vetted and found sound; it simply needs to be landed.
