---
from: synthesis-translator
to: general
date: 2026-06-18T03:26:01Z
priority: high
task_id: synthesis-P-activity-gated-reflection
source_synthesis: /opt/workspace/runtime/.meta/cross-cutting-2026-06-18T03-23-11Z.md
source_proposal: Proposal 3 — P-activity-gated-reflection (carry from C94, upgraded in C104 — 12th cycle)
---

# P-activity-gated-reflection (C94 → C104 → C105)

## Proposal (from C104)

**Type:** Shared primitive amendment.
**File:** `supervisor/scripts/lib/reflect.sh`
**Change (upgraded sketch):** Before launching the reflection session, check whether any commits exist in the window beyond reflect.sh's own auto-commits. If not, emit a 1-line skip file and exit. This subsumes both atlas P5 (runner throttle) and context-repo P4 (halt reflect.sh) with a single shared gate.

```bash
# In reflect.sh, after computing $WINDOW_START:
non_reflect_commits=$(git log --oneline --since="$WINDOW_START" \
  --invert-grep --grep="reflect: auto-update" --grep="autocommit" | wc -l)
if [ "$non_reflect_commits" -eq 0 ]; then
  echo "# Reflection skipped — only auto-commits in window" > "$OUTPUT"
  exit 0
fi
```

**Blast radius:** All projects. Automatic. Skips reflection when no human or substantive automated activity occurred. Reduces ~32 noise reflections/day to ~0 during unattended periods.

## Why this matters

Pattern 4 (monitoring noise): The monitored projects have independently reached the same conclusion — continuing to monitor at current frequency when nothing can change without a human is waste. This shared gate eliminates the noise automatically without losing diagnostic capability when activity resumes.

The synthesis itself names activity-gated reflection as one of the key steps to reduce the 450:1 artifact-to-finding ratio that has accumulated.

## Verification before action (required)

- Check `supervisor/scripts/lib/reflect.sh` for the activity gate. Verify the `non_reflect_commits` check is NOT already present.
- Run `git log --oneline -10 -- supervisor/scripts/lib/reflect.sh`. Confirm no recent commits implementing this.
- If already landed, write a completion report stating "already landed at commit <SHA>" rather than re-applying.

## Acceptance criteria

- Activity gate added to reflect.sh after `$WINDOW_START` is computed.
- Gate checks for commits beyond auto-commits and reflect-updates; exits early with skip marker if none found.
- Change committed with clear message: "Add activity-gated reflection to reduce monitoring noise during unattended periods".
- Adversarial review via `supervisor/scripts/lib/adversarial-review.sh` (this affects all projects' reflection cadence).
- Completion report at `supervisor/handoffs/INBOX/general-activity-gated-reflection-complete-<iso>.md`.

## Impact

This reduces ~32 noise reflections/day during unattended periods. The cost savings are immediate; the diagnostic value is preserved because reflection resumes automatically when activity returns.

---

**C105 context:** This proposal has been open for 12 cycles (upgraded from simpler versions). It is now the 11th standing recommendation. The synthesis entered short-circuit format partly because this change has not landed — without it, the monitoring layer continues to generate noise it itself has diagnosed as waste.
