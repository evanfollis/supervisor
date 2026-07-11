---
from: synthesis-translator
to: general
date: 2026-06-17T03:29:34Z
priority: medium
task_id: synthesis-translator-idempotent
source_synthesis: /opt/workspace/runtime/.meta/cross-cutting-2026-06-17T03-26-25Z.md
source_proposal: "Proposal 3: P-synthesis-translator-idempotent (carry from C101 — 3rd cycle)"
---

# P-synthesis-translator-idempotent — prevent duplicate handoff deposits

**Type:** Shared primitive fix.
**File:** `supervisor/scripts/lib/synthesis-translator.sh`
**Change:** Add slug-existence check before deposit.
**Blast radius:** Supervisor only. Low risk.
**Status:** 3rd synthesis cycle. Proposed in C101. Carries pattern from C102.

## Full proposal

The synthesis notes:

> **Rank: 5 (unchanged from C102).**
>
> No new translator deposits observed in this window's telemetry (only
> atlas runner events and session summaries). INBOX count stable at 198.
> The P-synthesis-translator-idempotent fix (C101 rec #25) remains
> unimplemented. ~60-70% of INBOX items are duplicates.

**Failure class:** Deposit mechanism with no idempotency gate.

## Current problem

When `synthesis-translator.sh` runs multiple times in close succession (e.g. if synthesize.sh triggers it twice), or if an agent re-submits the same prompt for some reason, duplicate handoff files get written to INBOX. This inflates the queue with duplicate work items that all require explicit archival to clean up.

Current INBOX count: 198+ items. Estimated 60-70% are duplicates of earlier proposals.

## Proposed change

In `supervisor/scripts/lib/synthesis-translator.sh`, before emitting each handoff file, check if a file with that proposal slug already exists in the target directory. If it does, skip deposit (or add to a duplicate count).

**Location:** The shell script calls `claude` with a prompt to emit the handoffs. The idempotency check should happen either:
1. In the shell script, after claude returns (check for `proposal-<slug>-*.md` before writing)
2. In the claude prompt itself (have claude verify file existence before Write)

Option 2 (in-prompt check) is preferred since the claude agent already has Read tool access. Add to `synthesis-translator-prompt.md`:

```markdown
Before writing each handoff file, check if it already exists:
- Read the target directory (handoff_dir or inbox_dir)
- Search for files matching `proposal-<slug>-*` pattern (any timestamp)
- If found, emit a log line "skipping duplicate: <filename>" and do not write
- Count duplicates in the final report
```

## Verification before action (required)

- Check `supervisor/scripts/lib/synthesis-translator-prompt.md`. Verify it does NOT currently include idempotency logic.
- Check recent handoff files in `supervisor/handoffs/INBOX/`. Look for duplicates (same proposal slug, different timestamps). If many exist, confirm the feature is not already implemented.
- Understand the current duplicate-ratio: ~60-70% of INBOX items are redundant. After the fix, verify that future synthesis runs do not create duplicates.

## Acceptance criteria

- Idempotency logic is added to either the shell script or the prompt template (prompt is preferred).
- Logic checks for `proposal-<slug>-*` pattern in target directory before writing.
- If duplicate found, skip write and log the skip.
- Logic counts and reports duplicates in translator's completion output.
- Change committed with message: "Add idempotency gate to synthesis-translator (prevent duplicate proposals)"
- No adversarial review required for this gate addition.
- Completion report at `runtime/.handoff/general-supervisor-synthesis-translator-idempotent-complete-<iso>.md`.

## Impact

- Prevents INBOX inflation from re-run synthesis cycles.
- Does not retroactively clean up existing 198+ items (that's separate work), but stops the leak.
- Estimated to reduce new synthesis deposits by ~60-70% if synthesis re-runs happen.

## Escalation

None expected. This is a check-before-write addition with no breaking changes.
