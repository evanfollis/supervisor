---
from: synthesis-translator
to: general
date: 2026-06-14T15:27:34Z
priority: medium
task_id: synthesis-reflect-push
source_synthesis: /opt/workspace/runtime/.meta/cross-cutting-2026-06-14T15-23-48Z.md
source_proposal: 3. P-reflect-push (carry from C95 — 4th cycle, PAST >3-CYCLE FLAG)
---

# P-reflect-push — Add optional autopush to reflection jobs

## Proposal

Amend `supervisor/scripts/lib/reflect.sh` to support optional automatic push to origin after successful CURRENT_STATE.md auto-commit during reflection runs. This addresses ~306 commits of workspace-wide divergence between local branches and origin.

The feature is opt-in via environment variable, so the infrastructure amendment is autonomous. Enabling it for specific projects requires principal authorization.

## Full proposal text from synthesis

**Type:** Shared primitive amendment.
**File:** `supervisor/scripts/lib/reflect.sh`

**What:** After successful CURRENT_STATE.md auto-commit, push to origin
if opt-in env var is set. Addresses ~306 commits of workspace-wide
divergence.

**Sketch (unchanged):**
```bash
if [[ "${REFLECT_AUTOPUSH:-false}" == "true" ]]; then
  git -C "$PROJECT_DIR" push origin \
    "$(git -C "$PROJECT_DIR" branch --show-current)" 2>/dev/null || true
fi
```

**Blast radius:** All projects. Opt-in per repo. Requires principal auth.

## Verification before action (required)

- Check `supervisor/scripts/lib/reflect.sh` to see if any autopush logic already exists.
- Verify the location where CURRENT_STATE.md is auto-committed in the script.
- Confirm no existing push logic would conflict with this addition.

## Acceptance criteria

- The autopush logic is added to `reflect.sh` after the successful CURRENT_STATE.md commit block.
- The feature is controlled by `REFLECT_AUTOPUSH` env var (defaults to false for safety).
- The push is non-fatal (uses `2>/dev/null || true` to avoid breaking the reflection on push failure).
- Commit message explains that autopush is opt-in infrastructure for reducing origin divergence.
- A note in the commit or subsequent handoff indicates which projects should have autopush enabled pending principal decision.

## Escalation

URGENT if:
- The reflect.sh structure has changed significantly and the commit location is unclear. Describe the actual commit patterns observed and ask for clarification.
- Any project already has custom push logic that would conflict. Name the project and the conflict.
- Principal has explicitly deferred origin push for any projects (check decisions/ for a defer). If so, respect that deferral.
