---
from: synthesis-translator
to: general
date: 2026-06-03T15:26:00Z
priority: high
task_id: synthesis-p-fpreflect-reflect-head-check
source_synthesis: /opt/workspace/runtime/.meta/cross-cutting-2026-06-03T15-23-08Z.md
source_proposal: P-fpreflect — Scope reflect.sh HEAD check to exclude archive operations (2 cycles in INBOX)
---

# P-fpreflect — Scope reflect.sh HEAD check to exclude archive operations

**Type:** Shared primitive update — `reflect.sh`.

**Sketch:** Narrow the dirty-tree/HEAD check to exclude legal archive operations:

```bash
# In reflect.sh, narrow the dirty-tree/HEAD check:
# Before: any diff from HEAD triggers URGENT
# After: filter out handoffs/ARCHIVE/ from the diff check
changed=$(git diff --name-only HEAD | grep -v '^handoffs/ARCHIVE/')
```

**Blast radius:** Supervisor only (automatic). Eliminates both `dirty-tree` and `mutated-head` false-positive URGENTs generated when reflection sessions legally archive INBOX items.

**Rationale:** Cycle 16 confirmed that `reflect.sh` now generates two distinct false-positive URGENT types (`URGENT-supervisor-reflection-dirty-tree.md` and `URGENT-supervisor-reflection-mutated-head.md`). Both originate from the same HEAD-check mechanism. The check cannot distinguish legal archive operations from unauthorized mutations. Scoping the check to exclude `handoffs/ARCHIVE/` eliminates the false positives while preserving the safety net for actual unauthorized changes.

## Verification before action (required)

- Read `/opt/workspace/supervisor/scripts/lib/reflect.sh` and check the current HEAD-check logic.
- If `handoffs/ARCHIVE/` is already filtered, write a completion report stating "archive filter already present" rather than re-applying.
- Check `/opt/workspace/runtime/.handoff/` for existing URGENT files. If any exist post-landing, the filter may need adjustment.

## Acceptance criteria

- `reflect.sh` contains a `grep -v '^handoffs/ARCHIVE/'` filter on the `git diff --name-only HEAD` output.
- The HEAD check logic now excludes changes to files in `handoffs/ARCHIVE/` from triggering the dirty-tree/mutated-head URGENT.
- Change committed with message: "Scope reflect.sh HEAD check to exclude archive operations; eliminate false-positive URGENTs (synthesis P-fpreflect)"
- Adversarial review via `supervisor/scripts/lib/adversarial-review.sh` — this is a safety-net refinement to a governance primitive.
- Next reflection cycle should not generate `dirty-tree` or `mutated-head` URGENTs when only `handoffs/ARCHIVE/` changes exist.
- Completion report at `runtime/.handoff/general-supervisor-synthesis-p-fpreflect-complete-<iso>.md` pointing back to this handoff and the source synthesis.

## Escalation

URGENT if:
- The filter is already present — verify and close.
- After landing, `dirty-tree` or `mutated-head` URGENTs still appear — the scope may need adjustment (e.g., different archive path, other safe-file patterns).
- The filter inadvertently blocks legitimate change detection — restore full checking and escalate for design review.
