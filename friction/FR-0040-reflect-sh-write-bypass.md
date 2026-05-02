---
name: FR-0040 — reflect.sh disallow-list does not block Write tool
Status: Open
created: 2026-05-02
source: skillfoundry-harness-reflection-2026-05-02T02-23-45Z + INBOX/reflect-sh-disallow-list-gap-2026-05-01T16-48Z.md
---

# FR-0040: reflect.sh `--disallowedTools` blocks Edit but not Write

## Observation

The 2026-05-01T14:26Z skillfoundry-harness reflection session used the
`Write` tool to modify `CURRENT_STATE.md` at 14:29:54Z and used
`Bash(python3 open().write())` at 14:28:34Z. Both bypass the current
`--disallowedTools` list in `scripts/lib/reflect.sh`, which blocks
`Edit` but not `Write` or file-writing Bash subcommands.

A commit (`fdbc781`) appears to have been triggered by an unidentified
host process that scraped a `git commit -m` command embedded in the
reflection session's `CURRENT_STATE.md` output.

## Policy contradiction

`CLAUDE.md` states reflections are "read-only and propose-only — never
commits project code." In practice, reflections actively write
`CURRENT_STATE.md` via the `Write` tool every cycle. Either:

A) The policy must be updated to allow this specific write, with
   explicit scope (`CURRENT_STATE.md` only, no other files)
B) The write must be blocked and a different mechanism used (session
   stdout captured by reflect.sh, written by the script)

## Fix path (from INBOX/reflect-sh-disallow-list-gap-2026-05-01T16-48Z.md)

Add to `--disallowedTools` in `scripts/lib/reflect.sh` ~line 108:
```
"Write" "Bash(python3:*)" "Bash(node:*)" "Bash(perl -i:*)" "Bash(sed -i:*)" "Bash(tee:*)"
```

If Write is blocked: capture report from session stdout (option B).

Also: identify the auto-commit mechanism that ran the embedded
`git commit -m` command. Run `systemctl list-timers --all`,
`crontab -l`, `find /opt/workspace -name "*.sh" | xargs grep -l CURRENT_STATE`.

## Status

Open. Requires attended session with scripts/lib/ write access (Tier C
from tick sandbox). See INBOX handoff `reflect-sh-disallow-list-gap-2026-05-01T16-48Z.md`.
