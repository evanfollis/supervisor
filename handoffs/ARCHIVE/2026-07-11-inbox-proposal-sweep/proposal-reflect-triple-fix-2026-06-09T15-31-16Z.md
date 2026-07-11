---
from: synthesis-translator
to: general
date: 2026-06-09T15:31:16Z
priority: high
task_id: synthesis-reflect-triple-fix
source_synthesis: /opt/workspace/runtime/.meta/cross-cutting-2026-06-09T15-27-48Z.md
source_proposal: reflect.sh triple-fix (P-self-sustaining-fix + P-reflect-hook-allowlist + P-write-block)
---

# reflect.sh triple-fix

## Problem

Three converged failure modes in `supervisor/scripts/lib/reflect.sh` create a self-sustaining observation loop:

1. **Inactivity check counts automation artifacts** (lines 57–67): The check counts telemetry events and JSONL files as "activity." The observation system's own artifacts (session-end hooks, autocommits, tick events) always satisfy the threshold, so supervisor never short-circuits. Result: ~18 Claude sessions/day from supervisor alone, ~32–36 total sessions/day, ~$2/day cost, zero output.

2. **Hook writes trigger false-positive dirty-tree URGENTs** (~line 172): The reflect.sh dirty-tree check flags any untracked or modified files, including those written by session-end hooks (CONTEXT.md, CURRENT_STATE.md, handoff ARCHIVE). Result: spurious URGENT escalations from hook writes instead of genuine code changes.

3. **`Write` gap in `--disallowedTools`**: Like synthesize.sh, reflect.sh's claude invocation blocks `Edit` but not `Write`. The LLM can write to historical reflection files or adjacent artifacts.

## Solution

Apply three independent fixes to `supervisor/scripts/lib/reflect.sh`:

### a) Exclude automation from inactivity check (lines 57–67)

Replace the TELEMETRY_COUNT logic to filter out automation events:

```bash
TELEMETRY_COUNT=$(tail -n 5000 "$WORKSPACE_TELEMETRY_DIR/events.jsonl" 2>/dev/null \
  | grep -F "\"$PROJECT\"" \
  | grep -v '"source":"session-end-auto-summary"' \
  | grep -v '"source":"reflect"' \
  | wc -l || true)

JSONL_RECENT=$(find "$SESSION_DIR" -maxdepth 1 -name '*.jsonl' \
  -not -name '*reflect*' -newermt "12 hours ago" 2>/dev/null | wc -l)
```

This excludes automation events (session-end summaries, reflect jobs themselves) from the activity count, so the check only triggers on genuine user/project activity.

### b) Filter hook writes from dirty-tree check (~line 172)

Add a filter to exclude known hook-generated files:

```bash
BEFORE_DIRTY_FILTERED=$(echo "$BEFORE_DIRTY" | grep -vE '(CONTEXT|CURRENT_STATE)\.md|handoffs/ARCHIVE/' || true)
AFTER_DIRTY_FILTERED=$(echo "$AFTER_DIRTY" | grep -vE '(CONTEXT|CURRENT_STATE)\.md|handoffs/ARCHIVE/' || true)
```

Then use `BEFORE_DIRTY_FILTERED` and `AFTER_DIRTY_FILTERED` in the subsequent comparison instead of the unfiltered versions. This prevents session-end hook writes (which are expected and harmless) from triggering false-positive dirty-tree escalations.

### c) Add `Write` to `--disallowedTools`

Locate the claude invocation in reflect.sh (search for `--disallowedTools`) and add `Write` to the list alongside `Edit` and `NotebookEdit`.

## Why this matters

- **Impact:** Reduces wasted sessions from ~36/day to ~4/day (dormant projects auto-short-circuit, supervisor stops recycling on its own artifacts)
- **Cost savings:** ~$1.50/day (~$10.50/week) on wasted observation cycles
- **Data quality:** Eliminates false-positive URGENTs from hook writes, reducing INBOX noise
- **Scope:** Independent of P1 (test artifact cleanup) — can land immediately

## Verification before action (required)

- Read `supervisor/scripts/lib/reflect.sh` and locate the inactivity check (~line 57) and dirty-tree check (~line 172)
- Verify the `--disallowedTools` list in the claude invocation
- Check `git log` to confirm reflect.sh has not already been patched with these fixes

## Acceptance criteria

- All three fixes applied to `supervisor/scripts/lib/reflect.sh` (~15 lines total)
- Change committed with message explaining the three fixes (automation filtering, hook write exclusion, Write constraint)
- Observe one full reflection cycle (12h) and confirm:
  - Supervisor is not generating URGENTs from hook writes
  - Wasted-session count drops (count events.jsonl entries from `reflect` source over 24h before/after)
- Completion report notes the observed impact on session count and cost

## Blast radius

All 8 projects (automatic via reflect.sh template). Reduces overall workspace observation overhead but does not change project behavior.

## Escalation

URGENT if:
- Telemetry format or event structure has changed since the proposal was written (check actual event.jsonl entries to verify `source` field names)
- The dirty-tree check is already filtering hook writes from another path — report "already landed" and close
- One of the three fixes conflicts with a more recent change to reflect.sh
