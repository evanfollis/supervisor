---
id: FR-0040
title: reflect.sh --disallowedTools does not block Write tool
status: Open
filed: 2026-05-02
source: supervisor-tick-2026-05-01T16-48-26Z (escalated), written 2026-05-02T06-48Z
projects: supervisor, all-reflected-projects
---

# FR-0040 — reflect.sh disallow-list incomplete (Write tool bypass)

## What happened

`--disallowedTools` in `scripts/lib/reflect.sh` blocks `Edit` but NOT `Write`
or `Bash(python3:*)`, `Bash(tee:*)`, etc. Reflections use the `Write` tool to
update `CURRENT_STATE.md` every cycle.

Concrete incident: The 2026-05-01T14:26Z skillfoundry-harness reflection wrote
`CURRENT_STATE.md` via both the `Write` tool (14:29:54Z) and `Bash(python3
open().write())` (14:28:34Z). A git commit -m command embedded in the resulting
CURRENT_STATE.md was executed by an unknown host process at 14:28:35Z, landing
commit fdbc781 to a project repo from a supposedly read-only reflection session.

## Policy contradiction

CLAUDE.md states: "Read-only and propose-only — never commits project code."
Operational reality: reflections write CURRENT_STATE.md every cycle via `Write`
tool. This is intentional behavior (maintaining current state) that contradicts
the declared policy.

## Resolution paths (two independent fixes needed)

### Fix 1 — Immediate: Tighten disallow-list in scripts/lib/reflect.sh ~line 108

Add to `--disallowedTools`:
  `"Write" "Bash(python3:*)" "Bash(node:*)" "Bash(perl -i:*)" "Bash(sed -i:*)" "Bash(tee:*)"`

If Write is blocked, the reflection report must be written via:
- Option A: `--output-file` if supported; script writes the file
- Option B: session outputs report to stdout; reflect.sh captures with `tee`

### Fix 2 — Structural: Remove ready-to-run git commands from CURRENT_STATE.md

Stop embedding `git commit -m "..."` in CURRENT_STATE.md instruction text.
Replace with prose instructions that require human intent to execute.

Also: identify the auto-commit mechanism (systemctl list-timers, crontab -l,
find scripts that grep CURRENT_STATE) that executed the embedded command.

Reference handoff: `supervisor/handoffs/INBOX/reflect-sh-disallow-list-gap-2026-05-01T16-48Z.md`
