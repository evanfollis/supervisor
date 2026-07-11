---
from: synthesis-translator
to: general
date: 2026-06-04T15:30:28Z
priority: medium
task_id: synthesis-reflect-sh-archive-scope
source_synthesis: /opt/workspace/runtime/.meta/cross-cutting-2026-06-04T15-27-05Z.md
source_proposal: P-fpreflect — Scope reflect.sh HEAD check to exclude archive operations
---

# Scope reflect.sh HEAD check to exclude archive operations

## Proposal body (from synthesis)

**Type:** Shared primitive update — `reflect.sh`.

**Blast radius:** Supervisor only (automatic). Eliminates both `dirty-tree` and `mutated-head` false-positive URGENTs.

## Context

The synthesis reports 2 false-positive URGENT variants confirmed in the current cycle related to archive operations within the reflect.sh HEAD check. These URGENTs are routed through the INBOX and degrade signal quality. Scoping the HEAD check to exclude archive operations (transient files created during reflect.sh execution but cleaned up by autocommit) eliminates these false positives.

This proposal has been in INBOX for **4 cycles** with zero landings. The synthesis notes this as one of 5 self-applicable proposals that "could be landed by a single attended executive session (~15 min of work, ~10 lines of code across 4 files)."

## Verification before action (required)

- Run `git log --oneline -10 supervisor/scripts/lib/reflect.sh` to verify this change hasn't landed via another path.
- Read the current state of `supervisor/scripts/lib/reflect.sh`. Identify the HEAD mutation check and confirm it doesn't yet exclude archive operations.
- If the change is already present, write a completion report stating "already landed" and close.

## Acceptance criteria

- Modify `supervisor/scripts/lib/reflect.sh`:
  - Scope the HEAD mutation detection to exclude files under `handoffs/ARCHIVE/` and other transient archive operations.
  - The scope may be a `--pathspec-exclude` pattern or an explicit allow-list of architecture-significant files (per the proposal intent: allow archive operations to proceed without false-positive URGENTs).
- Commit with message explaining the synthesis source (imperative mood: "Scope reflect.sh HEAD check to exclude archive operations — eliminate false-positive URGENTs").
- Verify that archive operations no longer generate `mutated-head` URGENTs.
- Completion report at `runtime/.handoff/general-synthesis-reflect-sh-archive-scope-complete-<iso>.md` pointing back to this handoff and source synthesis.

## Escalation

URGENT if:
- Primary verification reveals the change is already landed. Do not re-apply; write a completion report with the confirmed state.
- The change conflicts with a more recent decision in `supervisor/decisions/`. Do not force-apply; escalate with the conflict named.
- The scope of the change is unclear (what exactly counts as "archive operations"). Escalate with clarification needed from synthesis or CLAUDE.md.
