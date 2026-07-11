---
from: synthesis-translator
to: general
date: 2026-07-10T15:28:36Z
priority: medium
task_id: synthesis-p5-reflect-head-check-whitelist
source_synthesis: /opt/workspace/runtime/.meta/cross-cutting-2026-07-10T15-24-51Z.md
source_proposal: P5 (CARRY — C120, 18th cycle): Patch reflect.sh HEAD-check false positive
---

# P5: Patch reflect.sh HEAD-check false positive

**Type:** `reflect.sh` — whitelist autocommit SHAs in HEAD comparison.

**Blast radius:** Supervisor, synaplex. ~15 min.

## Background

Currently, reflect.sh (lines 154-168) compares HEAD before and after reflection to catch any unexpected mutations. If HEAD has changed, it emits a CRITICAL error and exits.

However, some projects (notably supervisor and synaplex) have autocommit hooks that advance HEAD during the reflection window. When this happens, the HEAD-check fires a false positive: it sees HEAD has advanced and treats it as a reflection session mutation, even though the mutation happened outside the reflection (via autocommit).

## Verification before action (required)

- Location: `/opt/workspace/supervisor/scripts/lib/reflect.sh` lines 154-168
- Current behavior: if `BEFORE_HEAD != AFTER_HEAD`, emit CRITICAL and exit 3
- Target behavior: whitelist autocommit SHAs (e.g., commits with message `autocommit <timestamp>`) so they don't trigger the false positive
- Check: `git log --oneline -20` in supervisor to verify autocommit commit messages exist

## Implementation notes

1. Define an autocommit SHA pattern (e.g., commit message contains "autocommit" or author is a bot user)
2. When comparing AFTER_HEAD to BEFORE_HEAD, resolve both to their base tree state before any autocommits
3. Alternatively: retrieve the list of autocommit SHAs since BEFORE_HEAD time, check if AFTER_HEAD is an autocommit commit on top of BEFORE_HEAD, and if so, allow it
4. Example logic:
   ```bash
   # Check if AFTER_HEAD is an autocommit of BEFORE_HEAD
   if git -C "$PROJECT_DIR" log --oneline "$BEFORE_HEAD..$AFTER_HEAD" | grep -q "^[^ ]* autocommit"; then
     # This is an autocommit on top of the pre-reflection HEAD, allow it
     echo "reflect[$PROJECT]: HEAD advanced by autocommit, allowed"
   elif [[ "$BEFORE_HEAD" != "$AFTER_HEAD" ]]; then
     # Unexpected mutation
     echo "reflect[$PROJECT]: CRITICAL — unexpected HEAD change"
     ...
   fi
   ```

## Acceptance criteria

- reflect.sh no longer fires false positives on autocommit-driven HEAD changes
- Non-autocommit HEAD changes still trigger the CRITICAL error
- Change committed with message: "Whitelist autocommit SHAs in reflect HEAD-check"
- Tested on supervisor (known to have autocommit hook)
- Completion report filed at `runtime/.handoff/general-reflect-head-whitelist-complete-<iso>.md`

## Escalation

If the autocommit detection heuristic is unclear (e.g., which commit pattern to match?), check recent supervisor git log to confirm the message format and provide that as the pattern.
