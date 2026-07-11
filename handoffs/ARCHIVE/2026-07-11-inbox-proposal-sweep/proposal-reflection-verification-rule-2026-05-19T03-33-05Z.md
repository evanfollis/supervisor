---
from: synthesis-translator
to: general
date: 2026-05-19T03:33:05Z
priority: medium
task_id: synthesis-reflection-verification-rule
source_synthesis: /opt/workspace/runtime/.meta/cross-cutting-2026-05-19T03-25-36Z.md
source_proposal: Proposal 3 (CARRIED from cycle 44, 2nd cycle) — Add verification rule to reflection prompts
---

# Proposal 3: Add verification rule to reflection prompts

## Background

Cycle 44 identified that reflections were accepting tick events and prior reflections as evidence of current file state, without verifying files directly. This cycle's supervisor reflection organically corrected this by citing `grep` and `ls` output instead of event claims. However, without a durable prompt amendment, this behavior is not guaranteed to persist. This proposal hardens the pattern by amending the reflection prompts.

## Implementation

Add the following block to **both** `/opt/workspace/supervisor/scripts/lib/reflect-prompt.md` and `/opt/workspace/supervisor/scripts/lib/reflect-supervisor-prompt.md`:

```markdown
**Verification rule:** When reporting the state of a file (frontmatter dates, content, counts), you MUST read the file directly. Do not cite tick events, session notes, or prior reflections as evidence of current file state. Event claims describe what a job intended to do; file reads describe what actually happened. If they conflict, the file read wins and the conflict is itself a finding.
```

**Placement:** Add this rule to the "Verification and evidence" or "Evidence standards" section of each prompt, or at the top of any section that discusses how to assess workspace state.

## Verification before action (required)

- Confirm both files exist: `ls /opt/workspace/supervisor/scripts/lib/reflect-prompt.md /opt/workspace/supervisor/scripts/lib/reflect-supervisor-prompt.md`
- Confirm the rule is not already present: `grep -c "Verification rule" /opt/workspace/supervisor/scripts/lib/reflect-*.md` — should return 0
- Note the current structure of each prompt to decide where the rule belongs (it should be in the "How to evidence claims" or "Standards" section if one exists)

## Acceptance criteria

- The verification rule is added to both `reflect-prompt.md` and `reflect-supervisor-prompt.md`
- Rule is phrased as a mandate ("you MUST"), not a suggestion
- Rule emphasizes the distinction between event claims (intended behavior) and file reads (actual behavior)
- Changes committed with message "reflect: add verification rule for file-state evidence"
- Completion report confirms both files were updated

## Escalation

None expected. This is a prompt-only amendment with no code changes.
