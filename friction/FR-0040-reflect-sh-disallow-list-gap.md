---
id: FR-0040
title: reflect.sh disallow-list gap — Write tool and shell write commands not blocked
status: Open
created: 2026-05-05
source: skillfoundry-harness reflection 2026-05-01T14:26Z (commit fdbc781)
---

# FR-0040: reflect.sh disallow-list gap

## What happened

The reflection session for skillfoundry-harness at 2026-05-01T14:26Z mutated `CURRENT_STATE.md` via the `Write` tool and `Bash(python3)`. Both bypass the current `--disallowedTools` list in `reflect.sh`. An unidentified host process subsequently scraped and executed a `git commit -m` command that was embedded in the mutated CURRENT_STATE.md, landing commit `fdbc781`.

The reflect.sh disallow-list at line 112 currently contains `"Edit" "NotebookEdit"` but is missing `"Write"` and destructive Bash forms (`Bash(python3:*)`, `Bash(sed -i:*)`, `Bash(tee:*)`, etc.).

## Impact

- Reflection jobs are intended to be read-only and propose-only. A Write-capable reflection job can corrupt project state.
- An inadvertent commit was landed by the auto-commit mechanism picking up shell commands embedded in CURRENT_STATE.md content.
- Any project in the reflection loop is vulnerable until the disallow-list is tightened.

## Fix

Two independent changes required:

**Fix 1** — Add `"Write"` to the `--disallowedTools` list at `scripts/lib/reflect.sh:112`. Also add `"Bash(python3:*)"`, `"Bash(sed -i:*)"`, `"Bash(tee:*)"`. Since Write is then blocked, the reflection report must be captured by the script itself (stdout capture via `tee` after `claude -p` exits).

**Fix 2** — Remove ready-to-run `git commit -m "..."` commands from CURRENT_STATE.md instructions to prevent the auto-commit mechanism from executing them. Replace with prose only.

## Status

Open — fix requires attended session (scripts/lib/ is Tier C). Routing handoff already in INBOX: `handoffs/INBOX/reflect-sh-disallow-list-gap-2026-05-01T16-48Z.md`.
