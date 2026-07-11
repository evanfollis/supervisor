---
from: synthesis-translator
to: general
date: 2026-06-13T15:31:37Z
priority: high
task_id: synthesis-p-handoff-resolution-checklist
source_synthesis: /opt/workspace/runtime/.meta/cross-cutting-2026-06-13T15-27-25Z.md
source_proposal: "Proposal 4 — P-handoff-resolution-checklist (4th cycle, PAST >3-CYCLE FLAG)"
---

# P-handoff-resolution-checklist

**Type:** CLAUDE.md amendment  
**File:** `/opt/workspace/CLAUDE.md`, section "Session Awareness"  
**Target:** Workspace charter (all projects inherit)  

## What

Add explicit guidance: when resolving an issue that has a corresponding handoff or URGENT file, delete the handoff file in the same session.

**Proposed text (to add after "After reading and acting on a handoff, delete the file."):**

```markdown
- **When resolving an issue that has a corresponding handoff or URGENT
  file, delete the handoff file in the same session.** Do not defer
  cleanup to a future session. The resolving session has the context to
  confirm the issue is closed; a future session must re-derive that
  context from scratch, which consistently fails to happen.
```

## Why

The stale-handoff pattern has been independently flagged by atlas, context-repository, and supervisor across 4+ cycles. Current state:

- 8 URGENT runtime files present (1 `.done`, 7 open)
- Oldest open: `URGENT-supervisor-event-stream-false-positive-2026-05-17.md` (~27 days)
- `URGENT-context-repository-structural-abandonment` now at 108h (4.5x FR-class breach)
- None consumed by an attended session in this window

The root cause: cleanup is deferred, and a future session cannot re-derive "is this actually closed?" without the original context. Making cleanup a co-requirement of resolution prevents the handoff from becoming a permanent stale artifact.

**This pattern has been flagged for 4+ cycles.** The stale-handoff accumulation is a workspace-wide hygiene failure, not a per-session lapse.

## Verification before action

- [ ] Read `/opt/workspace/CLAUDE.md` section "Session Awareness" to locate the existing handoff cleanup guidance
- [ ] Confirm the exact line "After reading and acting on a handoff, delete the file." exists (if wording differs, adapt the insertion point)
- [ ] Review runtime handoffs to verify the problem is real (check `/opt/workspace/runtime/.handoff/` and `supervisor/handoffs/INBOX/` for aged URGENT files)

## Acceptance criteria

- [ ] The proposed text is added to `Session Awareness` section, immediately after the existing cleanup guidance
- [ ] Text is clear and mandatory: "in the same session" and "do not defer" are explicit
- [ ] Change committed with message: "Charter: require handoff cleanup in resolving session (synthesis C96, P4)"
- [ ] No adversarial review required (behavioral guidance, text-only amendment)
- [ ] Completion report at `runtime/.handoff/general-workspace-synthesis-p-handoff-resolution-checklist-complete-<iso>.md`

## Escalation

**URGENT if:**
- The cleanup guidance is already in CLAUDE.md. Write completion report: "Already documented at <section, line>" and close.
- Verification reveals the stale-handoff problem is no longer present (queue has been flushed). Record that in the completion report (it would mean the problem was resolved by another path) and still apply the charter amendment as proactive prevention.
- The wording "in the same session" creates ambiguity for multi-stage handoffs that span sessions. Clarify or re-scope before committing.

## Remarks

Pure text amendment to the workspace charter. Low risk. Behavioral guidance, not enforcement. Recommended because the pattern has recurred across 4 independent projects and 4+ synthesis cycles without self-correction — explicit codification is the intervention.
