---
from: synthesis-translator
to: general
date: 2026-05-21T15:31:21Z
priority: medium
task_id: synthesis-adaptive-cadence
source_synthesis: /opt/workspace/runtime/.meta/cross-cutting-2026-05-21T15-24-47Z.md
source_proposal: "Proposal 5 (MEDIUM — 4th cycle): Adaptive reflection cadence for stasis projects"
---

# Adaptive reflection cadence for stasis projects

**Type:** Shared primitive change (configuration).

**Blast radius:** Projects marked `cadence=stasis` in `projects.conf` (opt-in).

**Problem:** Projects with zero commits over long windows (stasis state) generate useless reflections. Reflection consumes CPU, disk, and telemetry budget on projects that are not moving. However, there's a false-positive in the short-circuit logic: the reflection pass itself writes to its own JSONL, preventing the short-circuit from firing correctly (identified by atlas reflection at Cycle 50).

**Solution:** Add optional `cadence=stasis` field to `/opt/workspace/supervisor/scripts/lib/projects.conf`. Projects marked stasis will skip reflection passes when no commits occurred in the preceding N hours (TBD: 12h, 24h, or 72h — to be determined).

**Current state (VERIFIED):**
- `projects.conf` has no cadence field
- Format is currently: `<name>|<path>|<optional-prompt-template>`
- All projects run reflection on a fixed 12h schedule regardless of commit activity

**Fix locations:** 
1. `/opt/workspace/supervisor/scripts/lib/projects.conf` — add cadence field
2. `/opt/workspace/supervisor/scripts/lib/reflect.sh` — add short-circuit logic for stasis projects

**Proposed new format:**
```
# Format: <name>|<path>|<optional-prompt-template>|<optional-cadence>
# cadence values: (empty or omitted = default), stasis
atlas|/opt/workspace/projects/atlas||stasis
```

**Short-circuit logic:**
```bash
# In reflect.sh, before running the reflection prompt:
if [[ "$CADENCE" == "stasis" ]]; then
  COMMIT_WINDOW_HOURS=24  # or configurable
  LAST_COMMIT=$(git -C "$PROJECT_DIR" log --format=%at -1 2>/dev/null || echo 0)
  NOW=$(date +%s)
  HOURS_SINCE=$((( NOW - LAST_COMMIT ) / 3600))
  
  if [[ $HOURS_SINCE -gt $COMMIT_WINDOW_HOURS ]]; then
    echo "reflect[$PROJECT]: stasis mode — no commits in ${HOURS_SINCE}h, skipping reflection"
    exit 0
  fi
fi
```

**Bug noted in atlas reflection (Cycle 50):** The reflection's own JSONL write is being counted as "recent commit activity," causing the short-circuit to never fire for projects that have no actual commits. The git log command must be strictly against the repo's commit history, not side effects from reflection.

## Verification before action (required)

- ✓ Checked `projects.conf` — no cadence field present (verified at 15:24Z)
- ✓ Checked `reflect.sh` — no stasis short-circuit logic present
- ✓ Confirmed this is the 4th cycle carrying this observation
- ✓ Atlas reflection identified the JSONL-write false positive (Cycle 50, 14:18Z reflection)

## Acceptance criteria

- `projects.conf` format extended to support optional 4th field: `<name>|<path>|<optional-prompt>|<optional-cadence>`
- `reflect.sh` implements stasis short-circuit: skips reflection when no commits in N hours
- Short-circuit must use strict `git log` against repo commit history (not JSONL or other side effects)
- Updated `projects.conf` marks atlas, context-repository, and/or command as `cadence=stasis` (depending on which are idle)
- Change committed with message: "Add adaptive reflection cadence for stasis projects"
- Monitor Cycle 51 reflection output for stasis projects being skipped when inactive

## Escalation

Minor: synthesis doesn't specify which projects should start as stasis or what the window threshold (12h, 24h, 72h) should be. Recommend:
- **Atlas** → stasis (19 idle passes, zero attended sessions, principal A/B/C ~261h open)
- **context-repository** → stasis (24 idle passes, 10d since last commit)
- **Window threshold** → 24 hours (skip reflection if no commits in 24h)

If different thresholds are needed per project, that's a future refinement. Start conservative: 24h window, opt-in cadence=stasis for idle projects.
