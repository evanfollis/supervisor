---
id: FR-0040
title: reflect.sh --disallowedTools blocks Edit but not Write — reflections mutate project files
status: Open
created: 2026-05-01
updated: 2026-05-02
source: INBOX/reflect-sh-disallow-list-gap-2026-05-01T16-48Z.md
---

# FR-0040: reflect.sh disallow-list gap

## What happened

The skillfoundry-harness reflection session at 2026-05-01T14:26Z mutated
`CURRENT_STATE.md` via Write tool and `Bash(python3)`. The `--disallowedTools`
flag in `reflect.sh` blocks `Edit` but not `Write`. Write is a distinct tool
and requires an explicit entry in the disallow list.

Additionally, an unidentified host process scraped a `git commit -m "..."` command
embedded in `CURRENT_STATE.md`'s "suggested next action" section and executed it,
landing commit `fdbc781` in the skillfoundry-harness repo without an attended
session.

## Why it matters

The reflection job is supposed to be read-only and propose-only. Any write from
a reflection session bypasses the tier model and contaminates project repos with
unreviewed changes. The auto-commit mechanism means a single Write tool call can
propagate to a permanent commit.

## Two independent fixes needed

1. Add `"Write"` (and broad Bash patterns like `Bash(python3:*)`, `Bash(sed -i:*)`,
   `Bash(tee:*)`) to `--disallowedTools` in `scripts/lib/reflect.sh`
2. Stop embedding ready-to-run `git commit -m "..."` commands in CURRENT_STATE.md.
   Replace with prose descriptions of what to commit.

Note: adding `Write` to the disallow list means reflection reports must be written
differently. Preferred: reflection session outputs to stdout; `reflect.sh` captures
with `tee`.

## Pending

See INBOX/reflect-sh-disallow-list-gap-2026-05-01T16-48Z.md for fix details.
This is a Tier-C change (scripts/lib/) requiring an attended session.
