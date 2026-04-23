---
from: synthesis-translator
to: general
date: 2026-04-23T18-40-12Z
priority: high
task_id: synthesis-codify-saturation-exception
source_synthesis: /opt/workspace/runtime/.meta/cross-cutting-2026-04-23T15-24-05Z.md
source_proposal: Proposal 4 — Codify INBOX saturation exception in CLAUDE.md (4th cycle — mandatory)
---

# Codify INBOX saturation exception in CLAUDE.md (4th cycle — mandatory)

## Problem

Four consecutive syntheses have exercised an unrecorded exception to the escalation rules: when INBOX holds >5 unconsumed items sharing the same root cause, the synthesis job suppresses additional URGENT writes to INBOX for that root cause and instead records the suppression in the synthesis file itself. The synthesis file + `LATEST_SYNTHESIS` pointer become the escalation surface.

This exception is now de-facto policy and has been exercised without codification for 4 cycles. It should be explicitly documented in `/opt/workspace/CLAUDE.md` so that:
1. Future synthesis jobs know this is approved behavior (not a workaround)
2. The rationale is preserved (why this exception exists and when it applies)
3. The rule can be refined based on operational experience

## Proposed Fix

**File**: `/opt/workspace/CLAUDE.md`

**Location**: Section "Automated Self-Reflection Loop," after the carry-forward escalation paragraph.

**Content to append:**

```markdown
- **Saturation exception.** When INBOX holds >5 unconsumed items sharing the same root cause, the synthesis job may suppress additional URGENT writes to INBOX for that root cause and instead record the suppression in the synthesis file itself. The synthesis file + `LATEST_SYNTHESIS` pointer become the escalation surface. The suppression must be explicitly noted. This exception exists because adding noise to an unread queue degrades the signal the queue was designed to carry.
```

**Blast radius:** Synthesis job behavior only. Formalizes existing practice. All projects benefit indirectly through improved INBOX signal quality.

## Rationale

The synthesis file currently states: "Per the pattern established in the prior 3 syntheses, this synthesis also declines to write additional URGENT files to the saturated INBOX. The rationale is unchanged: adding item #32 to an unread 31-item queue where 29 items are noise is not escalation. **This synthesis file and the `LATEST_SYNTHESIS` pointer are the escalation surface.**"

This is now the canonical behavior. The rule should be visible in the charter so that:
- Synthesis jobs have explicit permission (not a workaround)
- Review and revision of the rule is intentional, not accidental
- The rule can be tuned based on operational evidence (e.g., INBOX size threshold, definition of "same root cause")

## Verification before action (required)

- Read `/opt/workspace/CLAUDE.md`. Locate the "Automated Self-Reflection Loop" section.
- Check if the saturation exception is already documented. Look for phrases like "Saturation exception," "INBOX holds >5," or "suppress additional URGENT writes."
- If the rule is already documented, read the existing text. If it matches the proposed content in intent, write a completion report stating "already documented." If it differs materially, escalate the difference.
- If the rule is not documented, proceed with the change.

## Acceptance criteria

- The proposed markdown is appended to the "Automated Self-Reflection Loop" section of `/opt/workspace/CLAUDE.md`.
- The text is in the same style and format as the surrounding rules (e.g., matching indentation, bold emphasis).
- The section now explicitly names the saturation exception, the threshold (>5 items), and the rationale.
- Change is committed with a message explaining the codification (e.g., "Codify INBOX saturation exception — de-facto policy for 4 cycles").
- Completion report confirms the rule is now documented and provides the commit SHA.

## Escalation

URGENT if:
- Verification shows the rule is already documented and matches. Skip with "already documented" note.
- Verification shows the rule is documented differently (e.g., different threshold, different rationale). Escalate the conflict with the existing text quoted.
- The CLAUDE.md file has restructured sections since the synthesis was written. Clarify the correct location for the new rule.
