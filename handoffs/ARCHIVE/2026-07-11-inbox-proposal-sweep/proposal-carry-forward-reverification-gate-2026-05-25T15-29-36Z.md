---
from: synthesis-translator
to: general
date: 2026-05-25T15:29:36Z
priority: high
task_id: synthesis-carry-forward-verification
source_synthesis: /opt/workspace/runtime/.meta/cross-cutting-2026-05-25T15-25-05Z.md
source_proposal: Proposal 4 (CARRY-FORWARD from C57): Add carry-forward re-verification to reflect prompt template
---

# Add carry-forward re-verification to reflect prompt template

## Proposal body

**Type:** Shared primitive fix (`reflect-prompt.md` and/or `reflect-supervisor-prompt.md`).

**What:** Before re-asserting an observation as "unresolved," re-run the canonical diagnostic. If clean, mark RESOLVED.

**Status:** 2nd synthesis cycle. 4 documented instances of the failure class (3 in harness + LCI bandwidth in researcher).

**Blocker classification:** **Attended-session-blocked.** Prompt template edit. No judgment or principal decision required.

**Blast radius:** All reflected projects (automatic).

**Why:** The reflection loop re-asserts stale carry-forwards without re-verification. This consumes bandwidth on known-broken items without distinguishing "still broken" from "was fixed between cycles." Requiring a re-run of the canonical diagnostic before re-asserting converts the carry-forward from advisory repetition to diagnostic signal. Harness 02:23Z observes: "3 documented instances: Codex PATH, preflight watcher, migrate.failure." Researcher 14:24Z adds a 4th instance: "LCI escalation re-stated identically for 9 cycles, consuming ~1,200 words of reflection bandwidth for a decision that requires one sentence from the principal."

## Verification before action (required)

- Check current state of reflect-prompt.md: `grep -c "carry.forward\|carry-forward\|re-verification\|re-run" /opt/workspace/supervisor/scripts/lib/reflect-prompt.md` — should return 0 if not yet landed.
- Check reflect-supervisor-prompt.md: `grep -c "carry.forward\|carry-forward\|re-verification\|re-run" /opt/workspace/supervisor/scripts/lib/reflect-supervisor-prompt.md` — should return 0 if not yet landed.
- If both return non-zero, mark as already-landed and close.

## Acceptance criteria

- At least one of the two prompt templates (reflect-prompt.md or reflect-supervisor-prompt.md) includes an explicit gate/instruction before re-asserting a carry-forward observation.
- The instruction should require the reflection to re-run the canonical diagnostic or check the most recent state before classifying the item as "still unresolved."
- If the diagnostic is clean (the issue was fixed), the reflection should mark it RESOLVED and remove it from carry-forwards.
- If the diagnostic still shows the issue, the reflection should re-assert with fresh evidence from the diagnostic run.
- Change committed with clear message referencing synthesis cycle 58 and the failure class.
- No adversarial review needed (prompt template amendment, no structural code change).

## Escalation

URGENT if:
- Primary verification reveals the re-verification gate is already present in either prompt template — mark as already-landed and close.
- The proposal conflicts with another pending reflection-loop change. Surface the conflict with filenames and dates.

---

## Completion report template

After landing, write a completion report at:
`/opt/workspace/runtime/.handoff/general-carry-forward-verification-complete-<iso>.md`

Include:
- Commit SHA where the change landed
- Which prompt template(s) were updated
- Brief note: "Carry-forward re-verification gate added to reflect prompts per synthesis C58 proposal 4"
- Reference back to this handoff
