---
from: synthesis-translator
to: general
date: 2026-05-27T03:28:16Z
priority: medium
task_id: synthesis-dispatch-deadline-enforcement
source_synthesis: /opt/workspace/runtime/.meta/cross-cutting-2026-05-27T03-24-35Z.md
source_proposal: Proposal 4 — Add synthesis-dispatch-deadline enforcement to reentry checklist
---

# Add synthesis-dispatch-deadline enforcement to reentry checklist

## Summary

The workspace has a 24h dispatch obligation for synthesis proposals (documented in `/opt/workspace/CLAUDE.md`). When the autonomous tick is functional, it serves as the primary consumer. When the tick is halted (as it currently is), there is no automatic enforcement path. This proposal adds an explicit reentry check so that an attended session cannot proceed with routine work until the synthesis dispatch obligation has been met or explicitly deferred.

## What to do

Edit `/opt/workspace/CLAUDE.md` under the "## Automated Self-Reflection Loop" section. Add a new subsection (after the existing subsection structure) called "### Synthesis dispatch deadline enforcement" with the following content:

```markdown
### Synthesis dispatch deadline enforcement

When the tick loop is halted and an attended session opens at workspace
root, check `LATEST_SYNTHESIS` age. If >20h old and no
`synthesis_reviewed` event exists for that file, dispatch the
synthesis as the first reentry action — before INBOX triage or other
backlog work. The 24h obligation cannot be met by a halted tick and
must be enforced at the attended-session boundary.

Operational check:
- `cat /opt/workspace/runtime/.meta/LATEST_SYNTHESIS` — points to the synthesis file
- `stat` the pointed-to file for age
- `grep -c synthesis_reviewed /opt/workspace/events/supervisor-events.jsonl | grep <synthesis-filename>` — confirm no review event yet
- If >20h old and not reviewed, read the synthesis immediately and emit a `synthesis_reviewed` event before proceeding to other work

The dispatch obligation is foundational to the feedback loop. An attended
session is the only remaining path when the tick is down. Do not defer or
skip this check.
```

## Why this matters

Current state: C60 synthesis was generated at 2026-05-26T15:32Z. The 24h dispatch deadline is 2026-05-27T15:32Z. No attended session has arrived. If no action occurs before that deadline, this will be the first recorded breach of the synthesis dispatch obligation.

The rule exists but has no enforcement mechanism when the tick is halted. An attended-session reentry check is the only fallback. This proposal makes that check explicit and mandatory.

## Verification before action (required)

- Confirm the section exists: `grep -n "Automated Self-Reflection Loop" /opt/workspace/CLAUDE.md` — it should exist
- Confirm no subsection with this name already exists: `grep -n "Synthesis dispatch deadline enforcement" /opt/workspace/CLAUDE.md` — should return nothing
- Check that `/opt/workspace/runtime/.meta/LATEST_SYNTHESIS` points to a synthesis file
- If verification fails, report the actual state and don't apply the patch

## Acceptance criteria

- `/opt/workspace/CLAUDE.md` has a new subsection under "Automated Self-Reflection Loop" explaining the enforcement requirement
- The subsection is clear and executable by a future attended session without additional context
- Change committed with message explaining the gap-closing rationale
- Verify: `grep -A 10 "Synthesis dispatch deadline enforcement" /opt/workspace/CLAUDE.md` returns the new text

## No adversarial review needed

This is documentation/policy amendment, not code logic. The prose clarity is more important than technical review.

## Escalation

URGENT if:
- The deadline has already passed (>24h since C60 synthesis) — apply the patch and also file a completion report explaining the late dispatch
- A synthesis_reviewed event was already emitted for this synthesis — verify and report "already dispatched"
