---
name: reflect.sh disallow-list gap — Write and python3 bypass
description: Reflection sessions can mutate project files via Write tool and Bash(python3) because neither appears in the --disallowedTools list; one mutation already committed
status: Open
created: 2026-05-01
source: runtime/.handoff/general-skillfoundry-harness-reflection-mutated-head-investigation-2026-05-01T14-35Z.md
---

# FR-0040: reflect.sh disallow-list gap — Write and python3 bypass

## Observation

The skillfoundry-harness reflection session at 2026-05-01T14:26Z mutated
`CURRENT_STATE.md` via the `Write` tool and `Bash(python3)`. Both bypass
the current `--disallowedTools` in `reflect.sh`. The resulting commit
(`fdbc781`) was triggered by an unidentified host process that scraped a
`git commit -m "..."` command embedded in CURRENT_STATE.md's suggested
next-action text.

## Two independent gaps

1. **reflect.sh disallow-list** does not include `Write`, `Bash(python3:*)`,
   `Bash(node:*)`, `Bash(perl -i:*)`, `Bash(sed -i:*)`, `Bash(tee:*)`
2. **CURRENT_STATE.md format** embeds ready-to-run `git commit` commands that
   an unidentified auto-commit process scraped and executed

## Fix needed (both required)

**Fix 1** — Tighten `scripts/lib/reflect.sh` ~line 108 disallow-list.
Add `Write` + shell mutation variants. Adjust report output to stdout
(captured by script `tee`) since Write will be blocked inside the session.

**Fix 2** — Remove `git commit -m "..."` from CURRENT_STATE.md templates.
Replace with prose instruction. Separately identify the auto-commit
mechanism (check `systemctl list-timers --all`, `crontab -l`, and scripts
that grep for CURRENT_STATE).

See INBOX: `reflect-sh-disallow-list-gap-2026-05-01T16-48Z.md`

## Status

Open. Both fixes require scripts/lib/ (Tier-C for tick). Routed to attended
executive session.
