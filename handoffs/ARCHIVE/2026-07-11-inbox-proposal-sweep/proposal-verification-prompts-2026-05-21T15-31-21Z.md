---
from: synthesis-translator
to: general
date: 2026-05-21T15:31:21Z
priority: medium
task_id: synthesis-verification-prompts
source_synthesis: /opt/workspace/runtime/.meta/cross-cutting-2026-05-21T15-24-47Z.md
source_proposal: "Proposal 3 (MEDIUM — 7th/5th cycle): Verification rules in reflection prompts"
---

# Add verification rules to reflection prompts

**Type:** Prompt amendment (governance/policy).

**Blast radius:** Supervisor tick and reflection jobs (automatic, prompt-only — no code changes).

**Problem:** Supervisor reflection and tick jobs are verifying against their own worktree state rather than against `origin/main`. This creates a self-confirmation loop where ticks verify a fix against their own isolated copy, declare success, and commit to the tick branch. Main doesn't have the fix.

**Evidence from Cycle 50:**
- Each of 5 ticks independently claimed "first real fix on main" for the same FR Status lines
- All claims were false — main did not have the fix
- Worktree isolation masks the ghost-write cascade (Root cause A in the synthesis)

**Root cause:** Prompts do not explicitly require verification against `origin/main` state. Reflection/tick agents verify locally by default, which gives false confidence.

**Fix locations:**
1. `/opt/workspace/supervisor/scripts/lib/reflect-supervisor-prompt.md`
2. `/opt/workspace/supervisor/scripts/lib/supervisor-tick-prompt.md`

**Proposed amendment:** Add a verification rule to both prompts:

```markdown
## Verification requirement

When checking whether a fix or change has been applied:
- **Verify against `origin/main`, not against your local worktree or branch.**
- Run: `git log --oneline origin/main -20` and search for the commit
- Or: `git show origin/main:<file>` and verify the target state is present
- Do not rely on your own worktree state to determine whether something landed on main

Why: Your worktree may contain unpushed commits, local changes, or isolated fixes that exist nowhere else. The source of truth for "did this land" is `origin/main`.
```

## Verification before action (required)

- ✓ Checked `reflect-supervisor-prompt.md` — no "verify against origin/main" rule present
- ✓ Checked `supervisor-tick-prompt.md` — no "verify against origin/main" rule present
- ✓ Confirmed this is the 7th/5th cycle carrying this observation (synthesis line 109)
- Both prompt files are writable, no external dependencies

## Acceptance criteria

- Both prompt files include an explicit verification rule directing agents to check `origin/main` state
- Rule appears in a high-visibility section (early in each prompt, before verification tasks)
- Phrasing is clear that worktree state is not authoritative (emphasize `origin/main` as the truth source)
- Change committed with message: "Add origin/main verification requirement to supervisor prompts"
- Monitor next reflection/tick cycle output for improved verification discipline

## Escalation

None anticipated. This is a pure prompt text addition with no code or logic changes. The change is defensive (tightens verification practice) and has no side effects.
