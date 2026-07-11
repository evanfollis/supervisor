---
from: synthesis-translator
to: general
date: 2026-05-20T03:30:22Z
priority: medium
task_id: synthesis-adaptive-cadence
source_synthesis: /opt/workspace/runtime/.meta/cross-cutting-2026-05-20T03-25-45Z.md
source_proposal: "Proposal 5 (NEW): Adaptive reflection cadence for stasis projects"
---

# Adaptive reflection cadence for stasis projects

## Context

The 12h reflection cadence is designed for projects with active development. For projects in maintenance stasis (no attended sessions, no commits, no telemetry), the reflection produces correct but redundant diagnosis. Four substantive reflections this cycle (command, atlas, context-repository, supervisor) explicitly describe saturation:

- **command**: "17th consecutive quiet window"
- **atlas**: "16th consecutive idle window"
- **context-repository**: "Twenty-first consecutive reflection pass with no human-initiated activity"
- **supervisor**: 5 automated ticks, zero attended sessions, zero structural changes on main

Each reflection generates JSONL transcript, writes CURRENT_STATE.md (which can't be committed due to the reflect.sh bug), and feeds the synthesis loop with repeat findings that displace novel signal.

## The Fix

**Files**: `supervisor/scripts/lib/reflect.sh` and `projects.conf`
**Target**: Implement adaptive cadence with a `stasis` mode for idle projects

### Step 1: Extend `projects.conf` format

Add optional `cadence` field (default `12h`):

```
# Format: <name>|<path>|<optional-prompt-template>|<optional-cadence>
# Cadence options: 12h (default), 24h, stasis
# stasis: skip reflection if no commits in 24h AND no JSONL sessions in window

atlas|/opt/workspace/projects/atlas|||24h
command|/opt/workspace/projects/command|||stasis
context-repository|/opt/workspace/projects/context-repository|||stasis
supervisor|/opt/workspace/supervisor|reflect-supervisor-prompt.md|stasis
```

### Step 2: Modify `reflect.sh` or `reflect-all.sh` to check cadence

Before invoking reflection for a project, check if stasis mode should skip it:

```bash
# In reflect-all.sh, before calling reflect.sh for each project:
CADENCE="${4:-12h}"  # Read from projects.conf field 4

if [[ "$CADENCE" == "stasis" ]]; then
  COMMITS=$(git -C "$PROJECT_DIR" log --since="24h" --oneline 2>/dev/null | wc -l)
  if [[ "$COMMITS" -eq 0 ]]; then
    # Check for recent sessions in the window
    SESSION_COUNT=$(find "$SESSION_DIR" -type f -name "*.jsonl" -mtime -1 2>/dev/null | wc -l)
    if [[ "$SESSION_COUNT" -eq 0 ]]; then
      echo "reflect[$PROJECT]: stasis mode, no commits or sessions in 24h — skipping"
      continue
    fi
  fi
fi
```

## Blast Radius

- Projects marked `stasis` in `projects.conf` (opt-in, no forced changes)
- Only affects reflection cadence; does not change what happens when reflection runs
- Unblocks synthesis loop from repeat findings during idle periods
- Affected projects: command (17 idle), atlas (16 idle), context-repository (21 idle), supervisor (5 ticks, 0 changes)

## Evidence

- command: 17 identical windows ("17 identical windows is sufficient evidence the current interval is wrong")
- atlas: 16 consecutive idle windows ("This reflection is structurally identical to the prior 15")
- context-repository: 21 consecutive passes with no activity ("three questions from prior cycles remain unanswered")
- Cost: each reflection writes CURRENT_STATE.md (stuck), generates transcript tokens, produces synthesis noise

## Verification before action (required)

- Read `supervisor/scripts/lib/projects.conf` to confirm format (should be pipe-delimited)
- Confirm the reflect.sh and reflect-all.sh runners exist at expected paths
- Check if cadence field is already present in projects.conf (search for `|||`)
- Check if stasis mode logic is already present in reflect.sh or reflect-all.sh (search for "stasis")
- If already implemented, mark as landed and close

## Acceptance criteria

- `projects.conf` is extended with optional 4th field for cadence (default `12h`)
- Cadence values: `12h` (default), `24h`, `stasis`
- `reflect.sh` or `reflect-all.sh` implements the stasis check (no commits + no sessions in 24h → skip)
- Four projects (atlas, command, context-repository, supervisor) are marked `stasis` in projects.conf
- Commit message explains the adaptive cadence rationale and the stasis mode intent
- Change tested by running the reflection loop (or code-reviewed for correctness)
- Completion report at `runtime/.handoff/general-supervisor-synthesis-adaptive-cadence-complete-<iso>.md`

## Escalation

URGENT if:
- Stasis mode is already implemented (landed by another path between synthesis and now)
- The reflect.sh runner cannot access projects.conf fields due to parsing constraints
- Principal has stated a preference for fixed-interval reflection despite idle periods
