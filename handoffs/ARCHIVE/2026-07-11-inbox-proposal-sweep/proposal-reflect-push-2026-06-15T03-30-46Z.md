---
from: synthesis-translator
to: general
date: 2026-06-15T03:30:46Z
priority: high
task_id: synthesis-p-reflect-push
source_synthesis: /opt/workspace/runtime/.meta/cross-cutting-2026-06-15T03-27-01Z.md
source_proposal: Proposal 3 — P-reflect-push
---

# P-reflect-push (carry from C95 — 5th cycle, PAST >3-CYCLE FLAG)

**Type:** Shared primitive amendment.
**File:** `supervisor/scripts/lib/reflect.sh`

## What

After successful CURRENT_STATE.md auto-commit, push to origin if opt-in env var is set. Addresses ~318 commits of workspace-wide divergence.

## Proposed code amendment to reflect.sh

Add this after the reflect.sh completes the CURRENT_STATE.md auto-commit:

```bash
if [[ "${REFLECT_AUTOPUSH:-false}" == "true" ]]; then
  git -C "$PROJECT_DIR" push origin \
    "$(git -C "$PROJECT_DIR" branch --show-current)" 2>/dev/null || true
fi
```

This should be added at the end of the reflection script, after the auto-commit gate but before the script exits. It is controlled by the REFLECT_AUTOPUSH environment variable (default: false for safety).

## Blast radius

All projects. Opt-in per repo via REFLECT_AUTOPUSH env var. Requires principal auth to set the env var on projects that should auto-push.

## Verification before action (required)

- Check if `REFLECT_AUTOPUSH` logic already exists in `supervisor/scripts/lib/reflect.sh`
- Verify the variable is appropriately safe (opt-in, default false)

## Acceptance criteria

- The REFLECT_AUTOPUSH conditional is added to reflect.sh
- The push is guarded to exit gracefully if it fails (`2>/dev/null || true`)
- Change committed with clear message referencing the synthesis source and divergence issue
- Documentation of which projects have REFLECT_AUTOPUSH=true env var
- Completion report at `runtime/.handoff/general-synthesis-p-reflect-push-complete-<iso>.md`

## Escalation

URGENT if:
- The logic already exists in reflect.sh (verify and close)
- The principal has not authorized which repos should auto-push (this will require principal decision via /remember or ADR)
