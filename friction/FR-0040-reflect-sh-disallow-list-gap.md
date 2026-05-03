---
name: FR-0040 reflect.sh Write bypass
description: reflect.sh --disallowedTools omits "Write", allowing reflection sessions to write CURRENT_STATE.md despite the "read-only, propose-only" policy.
status: open
created: 2026-05-01
cycles: 9
related:
  - INBOX: reflect-sh-disallow-list-gap-2026-05-01T16-48Z.md
  - INBOX: proposal-fix-reflect-write-bypass-2026-05-03T03-28-32Z.md
---

# FR-0040 — reflect.sh Write bypass

## What happened

`/opt/workspace/supervisor/scripts/lib/reflect.sh` line ~112 passes `--disallowedTools`
with `"Edit" "NotebookEdit"` but omits `"Write"`. Reflection sessions use the `Write` tool
to update `CURRENT_STATE.md` in project repos. The workspace CLAUDE.md states reflections
are "read-only and propose-only" — they are not.

This has been flagged in 9 consecutive synthesis cycles and 3+ INBOX proposals. The
one-line fix is known:
```diff
-    "Edit" "NotebookEdit" \
+    "Edit" "Write" "NotebookEdit" \
```

## Why it hasn't landed

`scripts/lib/` is Tier-C from all autonomous tick sessions. Fix requires attended session.
The Tier-B-auto authority proposal (INBOX: `proposal-tier-b-auto-authority-2026-05-02T18-50Z.md`)
would unblock this if approved.

## Status

Open. Awaiting principal decision on Tier-B-auto authority or direct attended-session fix.
