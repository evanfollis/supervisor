---
from: synthesis-translator
to: general
date: 2026-07-06T15:28:44Z
priority: high
task_id: synthesis-p2-activity-gated-reflection
source_synthesis: /opt/workspace/runtime/.meta/cross-cutting-2026-07-06T15-25-11Z.md
source_proposal: P2 (CARRY — C114, 15th cycle) Activity-gated reflection
---

# P2: Activity-gated reflection with carry-forward notes

**Type:** `reflect.sh` amendment — enhance activity-gating logic to emit carry-forward notes when observations are identical.

**Current state:** Lines 52–74 implement activity check that skips reflection on no commits/telemetry/session activity. Already working for 12 of 16 projects (token savings accumulating).

**Missing piece:** When skipping due to inactivity, the output should include a carry-forward note if the prior reflection's observations are identical to the previous cycle's observations. Currently just writes a bare "# Reflection skipped" placeholder.

**Proposed enhancement:**
- When reflection would short-circuit (no activity), check if the prior reflection file exists
- If it does, read the prior file's key observations
- If observations are materially identical to the prior cycle, emit a carry-forward note: `# Reflection skipped — no activity, prior observations unchanged`
- If they diverged, emit: `# Reflection skipped — no activity, but observations changed`
- This allows synthesis/executive to distinguish "no news" from "same-as-last-time"

**Blast radius:** All reflected projects (opt-in via `projects.conf`). Reduces token spend on dormant projects while preserving observability of state changes.

## Verification before action (required)

- Confirm `reflect.sh` lines 52–74 show the current activity-gating logic
- Verify 12 of 16 reflections are correctly short-circuiting per C128 synthesis report
- Check that prior reflection files exist in `$WORKSPACE_META_DIR` for each project

## Acceptance criteria

- Activity-gating logic remains in place (no regression)
- When skipping on inactivity, read prior reflection file and compare key observations
- Emit appropriate carry-forward note (unchanged vs. changed)
- Test on at least 2 dormant projects to verify output is written correctly
- Commit with message: "Enhance reflect.sh to emit carry-forward notes on identical observations per synthesis C128-P2"
- Completion report at `runtime/.handoff/general-activity-gated-reflection-complete-<iso>.md`
