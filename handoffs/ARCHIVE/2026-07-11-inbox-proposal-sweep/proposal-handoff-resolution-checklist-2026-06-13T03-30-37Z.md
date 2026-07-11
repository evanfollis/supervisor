---
from: synthesis-translator
to: general
date: 2026-06-13T03:30:37Z
priority: high
task_id: synthesis-handoff-resolution-checklist
source_synthesis: /opt/workspace/runtime/.meta/cross-cutting-2026-06-13T03-26-25Z.md
source_proposal: Proposal 4 — P-handoff-resolution-checklist
---

# P-handoff-resolution-checklist — Clarify handoff cleanup responsibility

**Status:** 3rd synthesis cycle. Now at >3-cycle flag threshold.
**Type:** CLAUDE.md behavioral guidance amendment (low risk).
**Evidence:** 7 URGENT files in runtime handoffs, at least 1 confirmed resolved but not deleted (atlas unpushed-commits, 4 reflection cycles unresolved).

## The problem

When an issue is resolved, the corresponding handoff or URGENT file is not consistently deleted. This creates stale escalation files that:

- Sit in the queue indefinitely (oldest runtime URGENT: 27 days, oldest INBOX URGENT: 36 days)
- Add noise to the escalation surface
- Create confusion about whether an issue is actually open or resolved

**Root cause:** No explicit guidance that the resolving session is responsible for cleanup. Future sessions assume stale handoffs are intentionally kept and don't clean them up.

**Evidence from synthesis:**
- 7 URGENT files present in runtime handoffs
- 1 confirmed resolved (atlas unpushed-commits) but still on disk
- "stale-handoff pattern has been independently flagged by atlas, context-repository, and supervisor"

## What to fix

File: `/opt/workspace/CLAUDE.md`, section "Session Awareness" (lines 175-182).

Add a new bullet after line 179 ("After reading and acting on a handoff, delete the file."):

```markdown
- **When resolving an issue that has a corresponding handoff or URGENT 
  file, delete the handoff file in the same session.** Do not defer 
  cleanup to a future session. The resolving session has the context to 
  confirm the issue is closed; a future session must re-derive that 
  context from scratch, which consistently fails to happen.
```

## Why this matters

- The resolving session is the only one with full context to confirm an issue is truly closed.
- Deferring cleanup to "later" consistently fails — stale handoffs accumulate indefinitely.
- Clear responsibility assignment removes ambiguity and prevents cleanup from becoming invisible work.

## Verification before action (required)

- Read `/opt/workspace/CLAUDE.md` at the "Session Awareness" section.
- Check if a bullet about handoff cleanup responsibility already exists.
- If yes, write a completion report: "Already present in CLAUDE.md / verified."
- If no, proceed with the amendment.

## Acceptance criteria

- The new bullet is added to the "Session Awareness" section after line 179.
- The text matches or closely paraphrases the proposed guidance.
- It emphasizes the resolving session's responsibility and the failure mode of deferral.
- Change committed with clear message explaining the synthesis source.
- Completion report written to `runtime/.handoff/general-workspace-synthesis-handoff-resolution-checklist-complete-<iso>.md`.

## Expected impact

- Future resolved issues will have their handoffs cleaned up immediately.
- Cleaner escalation surface (fewer stale URGENTs).
- Clearer process reduces accidental accumulation of stale files.
