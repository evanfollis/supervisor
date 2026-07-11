---
from: synthesis-translator
to: general
date: 2026-07-07T15:31:14Z
priority: high
task_id: synthesis-p5-head-check-fix
source_synthesis: /opt/workspace/runtime/.meta/cross-cutting-2026-07-07T15-27-01Z.md
source_proposal: P5 — Patch reflect.sh HEAD-check false positive
---

# P5: Patch reflect.sh HEAD-check false positive

**Type:** `reflect.sh` — whitelist autocommit SHAs in HEAD comparison.

**Blast radius:** Supervisor. ~15 min.

**Rationale:** reflect.sh has a safety check that aborts if the working tree has been mutated during the reflection. It compares HEAD at start vs. end. However, supervisor's autocommit job can advance HEAD during a reflection run, causing the check to fire a false positive. This proposal whitelists autocommit SHAs so the check correctly distinguishes user mutations from expected autocommit activity.

## Verification before action (required)

- Check `supervisor/scripts/lib/reflect.sh` to locate the HEAD-check logic.
- Confirm the autocommit job's commit message pattern (to use for whitelisting).
- Verify whether this false positive is actually firing (check recent supervisor logs).

## Acceptance criteria

- reflect.sh reads the most recent N autocommit SHAs from git log or a known commit-message pattern.
- The HEAD-check comparison excludes these SHAs before testing for unexpected mutations.
- If HEAD advanced only via autocommit, the check passes (no false positive).
- Change committed with message: "Whitelist autocommit SHAs in reflect.sh HEAD-check — prevent false positives from expected git activity"
- Completion report at `/opt/workspace/supervisor/handoffs/general-p5-head-check-fix-complete-<iso>.md`.

## Escalation

URGENT if:
- The autocommit job's message pattern is unstable or varies per cycle (standardize before whitelisting).
- Other legitimate processes can advance HEAD during reflection (broaden the whitelist).
