---
from: synthesis-translator
to: general
date: 2026-06-17T15:30:11Z
priority: high
task_id: synthesis-activity-gated-reflection
source_synthesis: /opt/workspace/runtime/.meta/cross-cutting-2026-06-17T15-26-36Z.md
source_proposal: Proposal 3 — P-activity-gated-reflection (UPGRADED from P-reflection-short-circuit, carry from C94 — 11th cycle)
---

# P-activity-gated-reflection (Pattern 4: Monitoring noise, self-throttling convergence)

**Type:** Shared primitive amendment.
**File:** `supervisor/scripts/lib/reflect.sh`
**Blast radius:** All projects. Automatic. Skips reflection when no human or substantive automated activity occurred. Reduces ~32 noise reflections/day to ~0 during unattended periods.

The synthesis reports that atlas and context-repository independently proposed throttling their own monitoring because reflection runs produce only noise during unattended periods. This proposal adds a shared activity gate to `reflect.sh` that skips reflection entirely when only auto-commits have occurred in the window.

**Proposed change (upgraded sketch):**

Before launching the reflection session, check whether any commits exist in the window beyond reflect.sh's own auto-commits. If not, emit a 1-line skip file and exit. This subsumes both:
- atlas P5 (runner throttle from 1h to 6h)
- context-repository P4 (halt reflect.sh entirely until attended session)

With a single shared gate.

**Exact implementation:**

Add this check in `reflect.sh`, after computing `$WINDOW_START`:

```bash
# Activity gate: skip reflection if only auto-commits in window
non_reflect_commits=$(git log --oneline --since="$WINDOW_START" \
  --invert-grep --grep="reflect: auto-update" --grep="autocommit" | wc -l)
if [ "$non_reflect_commits" -eq 0 ]; then
  echo "# Reflection skipped — only auto-commits in window" > "$OUTPUT"
  exit 0
fi
```

The existing reflection loop should proceed normally if `$non_reflect_commits > 0`.

## Verification before action (required)

- Read `supervisor/scripts/lib/reflect.sh` and check if an activity gate already exists (look for `non_reflect_commits` or similar logic).
- Check git log for any recent commit mentioning "activity-gated reflection" or "reflection skip gate".
- If either is true, write a completion report "already landed" rather than re-applying.

## Acceptance criteria

- The activity gate is added to `reflect.sh` before the reflection session launch.
- The gate detects when only auto-commits occurred and skips reflection by writing a 1-line skip marker.
- Change committed with message: "Add activity gate to reflect.sh: skip when only auto-commits in window"
- No adversarial review required (conditional skip logic, low complexity).
- Completion report at `runtime/.handoff/general-supervisor-synthesis-activity-gated-reflection-complete-<iso>.md` pointing back to this handoff and the source synthesis.

## Escalation

URGENT if:
- Verification reveals the gate is already in place. Write "already landed" completion report and close.
- The gate conflicts with a more recent decision about reflection cadence. Do not force-apply; escalate with the conflict named.

---

**Pattern context:** This is Pattern 4 (NEW refinement, upgraded from C103) from the synthesis. The monitoring layer has correctly identified its own futility: ~450:1 artifact-to-finding ratio, and two independent projects proposing to self-throttle. A shared activity gate subsumes both project-specific throttles and reduces workspace-wide monitoring noise by ~32 artifacts/day during unattended periods, while preserving diagnostic capability (reflection resumes immediately when activity resumes).
