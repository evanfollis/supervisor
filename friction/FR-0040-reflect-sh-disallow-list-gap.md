---
name: FR-0040 — reflect.sh --disallowedTools missing Write, allowing reflection to mutate project state
status: Open
filed: 2026-05-01 (ghost-claim); written to disk 2026-05-03
source: reflect-sh-disallow-list-gap-2026-05-01T16-48Z.md; cross-cutting-synthesis (7 cycles)
---

# FR-0040 — reflect.sh --disallowedTools missing Write, allowing reflection to mutate project state

## Pattern

Reflection sessions are intended to be "read-only and propose-only — never commits project
code." However, `scripts/lib/reflect.sh` has `--disallowedTools` that blocks `Edit` but not
`Write`. Reflection sessions can (and did) write to `CURRENT_STATE.md` and other project files.

## Evidence

- skillfoundry-harness reflection at 2026-05-01T14:26Z mutated `CURRENT_STATE.md` via Write
  tool — both bypass the current `--disallowedTools`.
- Commit `fdbc781` was triggered by an unidentified host process that scraped a `git commit -m`
  command embedded in CURRENT_STATE.md's "suggested next action" text.
- All 8 projects in the reflect loop are affected — CURRENT_STATE.md is written by reflections
  but never committed, causing perpetual uncommitted drift.

## Why it matters

1. Reflection sessions modifying project state violates the separation between read-only
   diagnosis and actionable change. The workspace's trust boundary for autonomous action
   depends on this separation being real.
2. The auto-commit mechanism in the reflect loop breaks when the working tree is dirty from
   the reflection's own writes — producing a catch-22.
3. An embedded shell command in CURRENT_STATE.md was auto-executed by a host process,
   creating a covert commit channel.

## Fix

In `scripts/lib/reflect.sh` line ~112, add to `--disallowedTools`:
```
"Write" "Bash(python3:*)" "Bash(node:*)" "Bash(perl -i:*)" "Bash(sed -i:*)" "Bash(tee:*)"
```

After adding `Write`, reflection reports must be captured via stdout + tee in reflect.sh
(not written by the session itself). A post-session step in reflect.sh can then write
CURRENT_STATE.md from the reflection output.

Also: remove ready-to-run `git commit -m "..."` commands from CURRENT_STATE.md templates.

## Status

Open. Requires change to `scripts/lib/reflect.sh` (Tier-C from tick sessions). Awaiting
attended/operator session. Proposed in 7 consecutive synthesis cycles.
