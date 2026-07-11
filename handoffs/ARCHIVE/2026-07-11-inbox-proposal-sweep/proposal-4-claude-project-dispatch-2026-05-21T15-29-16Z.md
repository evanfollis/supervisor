---
from: synthesis-translator
to: general
date: 2026-05-21T15:29:16Z
priority: medium
task_id: synthesis-claude-project-local-dispatch
source_synthesis: /opt/workspace/runtime/.meta/cross-cutting-2026-05-21T15-24-47Z.md
source_proposal: "Proposal 4 (MEDIUM — 16th cycle): CLAUDE.md amendment — project-local dispatch"
---

# CLAUDE.md amendment — project-local dispatch

**Type:** CLAUDE.md amendment.

**Status:** Unresolved.

**Blast radius:** All project sessions (automatic).

## Context

This proposal has been carried for 16 cycles without resolution. The synthesis does not specify the exact amendment text, only that it relates to "project-local dispatch."

**Related context from synthesis:**
- Dispatch obligation carry-forward: Cycles 47 (>38h) and 48 (>22h) past the charter 24h SLA with no dispatch or deferral
- Standing recommendation: "Dispatch obligation" listed as root cause C (Absent attended sessions)
- Escalation deadlock: carry-forward items route to INBOX, but INBOX saturation suppresses the escalation

## Interpretation

This proposal likely concerns clarifying or enforcing project-session dispatch obligations in the workspace charter. The synthesis references a 24h SLA for dispatch (per the supervisor charter) that is being violated.

**Likely content:** An amendment to `/opt/workspace/CLAUDE.md` that clarifies:
- When a project session receives a handoff, what are the dispatch obligations?
- What constitutes "dispatch" (vs. "received" vs. "acted on")?
- What is the SLA for acknowledgment/action?
- When should a project session escalate or defer rather than silently accept?

## Verification before action (required)

- Run `git log --oneline -20` on `/opt/workspace`. Check if an amendment addressing "dispatch" or "project-local" has landed.
- Read `/opt/workspace/CLAUDE.md`. Check if dispatch obligations are documented.
- If either is true, write a completion report stating "already landed" rather than re-proposing.

## What the receiving session should do

1. Read the last 3 synthesis files (Cycles 48, 49, 50) to understand the dispatch-obligation pattern.
2. Review `supervisor/decisions/` for any ADR that addresses dispatch SLAs or obligations.
3. Determine whether the amendment should target `/opt/workspace/CLAUDE.md` (workspace-level) or individual project CLAUDEs.
4. Draft the amendment text clarifying dispatch obligations and SLAs.
5. Route for adversarial review before landing.
6. Commit with message referencing the synthesis cycle(s).

## Acceptance criteria

- The amendment clarifies what "dispatch" means in the workspace handoff model.
- It establishes clear SLAs (the synthesis references a 24h SLA).
- It covers both "accept a handoff" and "escalate/defer a handoff" cases.
- Change committed with message explaining the dispatch-obligation governance (synthesis cycle reference).
- Completion report at `runtime/.handoff/general-supervisor-synthesis-dispatch-complete-<iso>.md`.

## Escalation

URGENT if:
- The amendment is based on an incorrect interpretation of the dispatch SLA — consult the supervisor charter first.
- The amendment conflicts with an existing rule in the supervisor charter — resolve the conflict with an ADR.
