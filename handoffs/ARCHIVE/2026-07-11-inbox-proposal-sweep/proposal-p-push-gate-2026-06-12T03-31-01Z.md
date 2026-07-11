---
from: synthesis-translator
to: general
date: 2026-06-12T03:31:01Z
priority: medium
task_id: synthesis-p-push-gate
source_synthesis: /opt/workspace/runtime/.meta/cross-cutting-2026-06-12T03-26-45Z.md
source_proposal: Proposal 3 — P-push-gate (carry from C92 — 2nd cycle)
---

# P-push-gate — Add opt-in push to autocommit pipeline

## Proposal

**Type:** Shared primitive addition.

**What:** Add an opt-in `git push` step to `supervisor/scripts/lib/supervisor-autocommit.sh` after successful Tier-A commits, gated on `SUPERVISOR_AUTOPUSH=true` env var.

**Sketch:**
```bash
if [[ "${SUPERVISOR_AUTOPUSH:-false}" == "true" ]]; then
  git -C "$SUP" push origin main 2>/dev/null || true
fi
```

Insert this block after line 85 (after the successful autocommit completion).

**Blast radius:** Supervisor only. Opt-in (requires env var set in systemd unit). No effect until explicitly enabled.

## Rationale (from synthesis)

**Problem:** Workspace-wide origin divergence growing monotonically. Every project with automated commits is drifting further from its remote:

| Project | Commits ahead | Commits behind |
|---------|--------------|----------------|
| supervisor | 249 | 2 |
| command | ~7 | 0 |
| context-repository | 4 | 0 |
| skillfoundry-harness | 4 | 0 |

**Evidence:**
- Total: ~265 commits across the workspace invisible to remote consumers
- The only resolution in the entire 12-hour window was atlas — one attended session ran `git push`
- This proves the mechanism works but demonstrates it is entirely human-gated
- With autocommit running every 2 hours on supervisor and reflect.sh auto-committing on every project, the divergence grows by ~12+ commits/day workspace-wide while push remains manual

**Failure class:** Automated write without automated publish. The autocommit contract says "commit to prevent dirty-tree gate deadlock" but stops at the local boundary. Push is a separate, unautomated step.

**Supervisor context:** 249 ahead means a fresh clone pulls state from weeks ago, and the 2-behind creates merge risk.

## Verification before action (required)

- Check current `supervisor/scripts/lib/supervisor-autocommit.sh` for any existing push logic
- Confirm no `SUPERVISOR_AUTOPUSH` environment variable is already present in the script or in `workspace-session@supervisor.service`
- Verify the current state: `git -C /opt/workspace/supervisor log --oneline origin/main..HEAD | wc -l` shows supervisor is ahead of origin

## Acceptance criteria

**Code changes:**
- The push gate block is added to `supervisor/scripts/lib/supervisor-autocommit.sh` (suggested location: after line 85, after successful commit log output)
- The gate checks `SUPERVISOR_AUTOPUSH` env var with default `false`
- Push attempts to `origin main` only if the var is explicitly true
- Push failure is soft (does not fail the autocommit; uses `|| true`)
- Commit message explains this adds the capability for manual env-var enablement per synthesis

**Integration:**
- NOTE: Env var enablement in systemd unit is PRINCIPAL-SCOPE — this handoff covers CODE ONLY
- The env var `SUPERVISOR_AUTOPUSH=true` must be set in `workspace-session@supervisor.service` by the principal (requires explicit authorization per synthesis)
- Once enabled at the principal's discretion, the push happens automatically on next autocommit cycle

**Testing:**
- With `SUPERVISOR_AUTOPUSH` unset (default), autocommit completes without pushing
- Code review recommended (touches push path; coordinates with principal credential/policy decision)

## Escalation

URGENT if:
- Verification reveals the push gate is already present in supervisor-autocommit.sh
- A recent decision contradicts opt-in autopush (check `supervisor/decisions/`)
- The push gate blocks on something other than the env var check (should be a no-op until enabled)
