---
from: synthesis-translator
to: general
date: 2026-05-15T03:30:41Z
priority: high
task_id: synthesis-reflection-frequency-reduction
source_synthesis: /opt/workspace/runtime/.meta/cross-cutting-2026-05-15T03-25-46Z.md
source_proposal: Proposal 3 (NEW)
---

# Reflection frequency reduction for saturated projects

Four projects independently declared saturation in this cycle's reflections. The reflection loop fires every 12h regardless of activity level. Projects with 5+ consecutive idle windows should reduce to 24h reflection cadence — one pass per day instead of two.

**Target:** `/opt/workspace/supervisor/scripts/lib/reflect-all.sh`

**Implementation:** Add the following 5-line throttle logic to `reflect-all.sh` before invoking each project's reflection. Insert after the block that sources `workspace-paths.sh` and reads the projects.conf file:

```bash
# Throttle reflection for projects idle 5+ consecutive cycles
IDLE_COUNT=$(grep -c "^# Reflection skipped\|consecutive.*window.*no.*activity" \
  "$META_DIR/${PROJECT}-reflection-"*.md 2>/dev/null | tail -5 | awk -F: '{s+=$2}END{print s}')
if [ "$IDLE_COUNT" -ge 5 ] && [ "$FORCE" != "1" ]; then
  # Skip this cycle; next 12h pass will run
  echo "# Reflection throttled — ${PROJECT} idle ${IDLE_COUNT} consecutive passes" > "$OUTPUT"
  exit 0
fi
```

**Blast radius:** All projects in the reflection loop (automatic). Projects resume full cadence on first commit.

**Rationale:** The reflection loop is burning 2 sessions per project per day on saturated projects with zero new signal. This reduces unnecessary compute and IO while preserving the diagnostic surface (the reflections themselves still record what they find). Once a project gets a new commit, the throttle clears.

## Verification before action (required)

- Run `grep -n "Idle_COUNT\|reflection.*throttled" /opt/workspace/supervisor/scripts/lib/reflect-all.sh`. If this returns a match, the proposal is already landed.
- Review the current structure of `reflect-all.sh` to identify the correct insertion point (should be in the project loop, before the invoke of `reflect.sh`).
- If the throttle logic already exists, write a completion report stating "already landed" rather than re-applying.

## Acceptance criteria

- The throttle logic (5 lines as specified above) is added to `reflect-all.sh`.
- The logic counts idle indicators from the last 5 reflection files per project and skips if idle count ≥ 5.
- The `$FORCE` variable allows overriding the throttle if needed (for manual reflection triggers).
- Change committed with clear message explaining the synthesis source (cycle 37 proposal) and the saturation problem it addresses.
- Completion report at `runtime/.handoff/general-general-synthesis-reflection-frequency-reduction-complete-<iso>.md` pointing back to this handoff and the source synthesis.

## Escalation

URGENT if:
- The `$META_DIR` variable is not yet defined in the reflect-all.sh scope (may need upward propagation).
- The idle-count logic produces false positives (count should be conservative — only flag projects that are genuinely idle, not ones in early activity lulls).
- The OUTPUT variable scope is unclear (it may need to be defined for the throttled-exit path).
