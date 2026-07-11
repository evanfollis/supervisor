---
from: synthesis-translator
to: general
date: 2026-05-21T03:29:20Z
priority: medium
task_id: synthesis-verification-rules-reflection-prompts
source_synthesis: /opt/workspace/runtime/.meta/cross-cutting-2026-05-21T03-24-44Z.md
source_proposal: "Proposal 3 (MEDIUM — 6th/4th cycle): Verification rules in reflection prompts"
---

# Verification rules in reflection prompts

**Full sketch:** Cycle 47, Proposal 3. Refer to `/opt/workspace/runtime/.meta/cross-cutting-2026-05-20T15-27-25Z.md` for the concrete prompt amendment specification.

**Status:** Partially self-correcting. Prompt amendment remains the durable fix.

**Blast radius:** All reflection jobs (automatic, prompt-only).

---

## Verification before action (required)

- Fetch cycle 48 synthesis and locate "Proposal 3" to extract the concrete prompt amendment.
- Verify that this amendment has NOT been applied to `supervisor/scripts/lib/reflect.sh` by searching for the key verification-rule language in the reflection prompt template.
- Run `git log --oneline supervisor/scripts/lib/reflect.sh | head -10` and check for recent commits mentioning verification rules.
- If the amendment has already landed in main or is present in the file, write a completion report stating "already landed at <commit>" rather than re-applying.

## Acceptance criteria

- The prompt amendment from cycle 47 is identified and applied to the reflection prompt template in `supervisor/scripts/lib/reflect.sh`.
- Change committed with clear message: `reflect: add verification rules to reflection prompt per synthesis cycle 47/49`
- Adversarial review via `supervisor/scripts/lib/adversarial-review.sh` optional for prompt changes.
- Completion report at `runtime/.handoff/general-supervisor-synthesis-verification-rules-complete-<iso>.md` pointing back to this handoff.

## Escalation

URGENT if:
- Cycle 48 synthesis cannot be located or Proposal 3 is not found in it (indicates broader synthesis carry-forward issue).
- The prompt amendment conflicts with more recent reflection changes made in another cycle.
