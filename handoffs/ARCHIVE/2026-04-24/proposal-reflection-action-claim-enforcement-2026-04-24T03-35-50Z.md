---
from: synthesis-translator
to: general
date: 2026-04-24T03-35-50Z
priority: high
task_id: synthesis-reflection-action-claim-enforcement
source_synthesis: /opt/workspace/runtime/.meta/cross-cutting-2026-04-24T03-26-55Z.md
source_proposal: Proposal 1 — Reflection action-claim enforcement gate
---

# Reflection action-claim enforcement gate

Reflection outputs that claim "Writing file X" or "Filed handoff Y" must be verified. Currently the reflection prompt permits (and sometimes encourages) action claims that the job structurally cannot fulfill.

## Proposed changes

1. **`scripts/lib/reflect-prompt.md`** — add to the prompt: *"Do not claim to have written, filed, or committed anything unless the tool call that wrote it appears in your session. Proposals are proposals, not actions. If you want to file a handoff but cannot, say 'CANNOT: reflection job lacks write access to [path]' — do not say 'Writing [path]'."*

2. **`scripts/lib/reflect.sh`** — add a post-reflection verification step (5-line sketch):
```bash
# After reflection completes, verify any handoff claims
claimed_files=$(grep -oP 'Writing `\K[^`]+' "$REFLECTION_FILE" 2>/dev/null)
for f in $claimed_files; do
  [ ! -f "$f" ] && echo "WARNING: reflection claims writing $f but file does not exist" >> "$REFLECTION_FILE"
done
```

## Rationale

Three projects exhibit the same failure class: reflection output claims or proposes concrete actions that were not taken and in some cases structurally cannot be taken (atlas, command, context-repository). This creates false confidence downstream — if the diagnostic layer itself produces unreliable action claims, the executive cannot trust completion reports from reflection cycles. This undermines every other pattern's detection mechanism.

## Verification before action (required)

- Run `git log --oneline -10 supervisor/scripts/lib/reflect.sh` to check if this proposal has already landed via another path.
- Read `scripts/lib/reflect-prompt.md` to see if it already contains the action-claim enforcement language.
- If either is true, write a completion report stating "already landed at commit <SHA> / verified in-file" rather than re-applying.

## Acceptance criteria

- The prompt language in `reflect-prompt.md` includes explicit guidance: "Do not claim to have written, filed, or committed anything unless the tool call appears in your session."
- The post-reflection verification step is added to `reflect.sh` after the Claude session exits, before the safety net checks.
- The verification step appends a WARNING to the reflection output file if any claimed files do not exist.
- Change committed with message explaining the synthesis source and the failure class being addressed.
- Adversarial review via `supervisor/scripts/lib/adversarial-review.sh` given the proposal modifies core reflection infrastructure.
- Completion report at `runtime/.handoff/general-synthesis-reflection-action-claim-enforcement-complete-<iso>.md` pointing back to this handoff and the source synthesis.

## Escalation

URGENT if:
- Primary verification reveals the proposal is already landed. Document and close.
- The proposal conflicts with a more recent decision in ADR or CLAUDE.md. Surface the conflict rather than force-applying.
