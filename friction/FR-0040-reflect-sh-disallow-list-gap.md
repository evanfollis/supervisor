# FR-0040: reflect.sh disallow-list gap — Write and python3 bypass reflection sandbox

Captured: 2026-05-01T14:35Z
Source: general-skillfoundry-harness-reflection-mutated-head-investigation
Status: open

## What happened

The reflection session for skillfoundry-harness at 2026-05-01T14:26Z used the
Write tool and `Bash(python3)` to mutate `CURRENT_STATE.md` — both bypass the
current `--disallowedTools` in `reflect.sh`. The commit that landed (`fdbc781`)
appears to have been triggered by an unidentified host process that scraped a
`git commit -m "..."` command embedded in CURRENT_STATE.md's "suggested next
action" text and executed it.

## Why it matters

The reflection job is intended to be read-only and propose-only. A reflection
session that can write files and trigger commits via embedded shell commands
is a safety regression: it can mutate project state under the cover of
"reflection," bypassing the governance boundary that separates diagnosis
from execution.

## Root cause / failure class

Two independent gaps:
1. `--disallowedTools` in reflect.sh does not include `Write` or `Bash(python3:*)`,
   allowing file mutation inside the reflection session.
2. An unidentified host process (timer? cron? autocommit?) scrapes shell commands
   embedded in CURRENT_STATE.md and executes them. This mechanism is unknown.

## Fix needed (two parts, Tier-C — attended session required)

### Fix 1: Tighten disallow-list in scripts/lib/reflect.sh ~line 108
Add: `"Write" "Bash(python3:*)" "Bash(node:*)" "Bash(perl -i:*)" "Bash(sed -i:*)" "Bash(tee:*)"`
Note: disallowing Write means the session must write reports to stdout; reflect.sh
captures with tee.

### Fix 2: Remove ready-to-run git commands from CURRENT_STATE.md templates
Until the auto-commit mechanism is identified, CURRENT_STATE.md instructions
should use prose ("commit when ready") not literal `git commit -m "..."` commands.
The mechanism identification: `systemctl list-timers --all`, `crontab -l`,
`find /opt/workspace -name "*.sh" | xargs grep -l CURRENT_STATE`.

## Remaining work

Both fixes require editing scripts/lib/ (Tier-C). Route to attended session.
Identify the auto-commit mechanism before the next reflection cycle.
