# FR-0040: reflect.sh missing Write in --disallowedTools

Captured: 2026-05-03T06:50Z
Source: attended-tick-2026-05-03T06-50-00Z
Status: open

## What happened

`/opt/workspace/supervisor/scripts/lib/reflect.sh` line 112 lists `"Edit" "NotebookEdit"`
in `--disallowedTools` but omits `"Write"`. Reflection sessions are supposed to be
read-only and propose-only per CLAUDE.md, but every reflection run can write files using
the Write tool. The CURRENT_STATE.md files in project repos are written by reflection sessions
via the Write tool — this is the mechanism bypassing the policy.

## Evidence

- Skillfoundry-harness reflection 2026-05-03T02:24Z: "reflect.sh lines 100–120 confirm: Write
  is NOT in the disallow list."
- Proposal to fix: `proposal-fix-reflect-write-bypass-2026-05-03T03-28-32Z.md` in INBOX.
- This observation has appeared in 9 consecutive reflection cycles.

## Fix

One token addition at reflect.sh:112:
```diff
-    "Edit" "NotebookEdit" \
+    "Edit" "Write" "NotebookEdit" \
```

Blocked by: Tier-C classification of `scripts/lib/`. Requires attended session or
Tier-B-auto authority approval (principal item #4 in 2026-05-03T02-47Z principal-decisions).
