---
from: synthesis-translator
to: general
date: 2026-07-06T15:28:44Z
priority: medium
task_id: synthesis-p5-reflect-head-whitelist
source_synthesis: /opt/workspace/runtime/.meta/cross-cutting-2026-07-06T15-25-11Z.md
source_proposal: P5 (CARRY — C120, 10th cycle) Patch reflect.sh HEAD-check false positive
---

# P5: Patch reflect.sh HEAD-check false positive

**Type:** `reflect.sh` amendment — whitelist autocommit SHAs in HEAD comparison.

**Current state (lines 91–94, 159–163):**
- `BEFORE_HEAD` is captured before invoking Claude reflection session
- If `AFTER_HEAD` differs from `BEFORE_HEAD`, reflect.sh raises CRITICAL error and aborts
- This is a safety net against reflection accidentally mutating the repo despite `--disallowedTools`

**Problem:** Supervisor's `autocommit.sh` may have committed governance artifacts between reflection's start and end, advancing HEAD legitimately. The current check treats this as a reflection-layer mutation (false positive).

**Proposed fix (lines 115–119):**
- When comparing HEAD, whitelist known autocommit SHAs
- Get the list of recent autocommit SHAs from supervisor git history (last 20 commits starting with "autocommit")
- If `AFTER_HEAD` is one of those known autocommit SHAs, allow it and log: `reflect[$PROJECT]: HEAD advanced by supervisor autocommit (expected)`
- Otherwise, keep the current CRITICAL error behavior

**Blast radius:** Supervisor reflection only. ~15 min implementation.

## Verification before action (required)

- Confirm `reflect.sh` lines 91–94 capture BEFORE_HEAD correctly
- Confirm lines 159–163 contain the HEAD comparison that triggers the false positive
- Verify supervisor git log has recent autocommit entries with predictable commit message pattern ("autocommit 20XX-...")

## Acceptance criteria

- Get list of recent autocommit SHAs: `git -C /opt/workspace/supervisor log --oneline -20 | grep "^[0-9a-f]\+ autocommit" | awk '{print $1}'`
- Store as `AUTOCOMMIT_SHAS` array in reflect.sh
- When comparing HEAD, check: `if [[ "$AFTER_HEAD" =~ ^(${AUTOCOMMIT_SHAS[*]}|$BEFORE_HEAD)$ ]]`
  - If match: log "HEAD advanced by supervisor autocommit (expected)" and continue
  - If no match: keep current CRITICAL error behavior
- Test by running reflect on a project while supervisor is committing (should pass)
- Commit with message: "Whitelist autocommit SHAs in reflect.sh HEAD-check per synthesis C128-P5"
- Completion report at `runtime/.handoff/general-reflect-head-whitelist-complete-<iso>.md`
