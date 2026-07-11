---
from: synthesis-translator
to: general
date: 2026-05-21T15:29:16Z
priority: medium
task_id: synthesis-verification-rules-reflect-prompts
source_synthesis: /opt/workspace/runtime/.meta/cross-cutting-2026-05-21T15-24-47Z.md
source_proposal: "Proposal 3 (MEDIUM — 7th/5th cycle): Verification rules in reflection prompts"
---

# Verification rules in reflection prompts

**Type:** Prompt amendment.

**Change:** Add "verify against origin/main, not worktree" to `reflect-supervisor-prompt.md` and `supervisor-tick-prompt.md`.

**Blast radius:** Supervisor tick and reflection jobs (automatic, prompt-only).

## Context

The synthesis names a critical diagnostic failure: the supervisor reflection and tick jobs verify their findings against their own worktree state, not against origin/main. This creates a ghost-write cascade with self-confirmation:

1. A tick generates code in its own worktree
2. The tick-end verification reads the worktree and reports "first real fix on main"
3. Main doesn't have the fix; the tick's worktree is isolated
4. The next tick's reflection reads the same worktree isolation and independently reports "first real fix"
5. Each tick believes it has landed changes when it has only landed them locally

The synthesis documents 5 ticks in a single 12h window each claiming "first real fix on main" for the same issue — all false because they were verifying against worktree state, not main.

## Fix

Add explicit verification language to the reflection and tick prompts:

**For `reflect-supervisor-prompt.md`:**
Add a section to the "Verification" or "Artifacts to read" section that says:
> When verifying whether a fix has been applied, always check `git -C /opt/workspace/supervisor log --oneline -10 | grep <description>` against origin/main (not the current worktree). If the commit is not visible in origin/main history, the fix has not been deployed.

**For `supervisor-tick-prompt.md`:**
Add a similar section that emphasizes:
> Verify changes by reading `git log origin/main` after pushing, not by examining the tick's own worktree. A change in your worktree that is not in origin/main is not yet landed.

The intent is to make the prompts explicitly discriminate between "what I built locally" and "what is now on main."

## Verification before action (required)

- Run `git log --oneline -20` on `/opt/workspace/supervisor`. Check if this amendment has already landed.
- Read `/opt/workspace/supervisor/scripts/lib/reflect-supervisor-prompt.md` and `supervisor-tick-prompt.md`. Check if the verification language exists.
- If either is true, write a completion report stating "already landed at commit <SHA> / verified in-file" rather than re-applying.

## Acceptance criteria

- Both reflection and tick prompts contain explicit language distinguishing worktree state from origin/main state.
- The language includes concrete git commands (e.g., `git log origin/main --oneline`) that reflection/tick jobs should use.
- Change committed with message explaining the amendment purpose (synthesis cycle reference).
- Completion report at `runtime/.handoff/general-supervisor-synthesis-verify-prompts-complete-<iso>.md` pointing back to this handoff.

## Escalation

URGENT if:
- The prompt change makes reflection/tick jobs unable to complete (e.g., the git commands fail in the sandboxed environment) — document the failure and revert.
- The added language conflicts with an existing prompt section — resolve the conflict or consolidate.
