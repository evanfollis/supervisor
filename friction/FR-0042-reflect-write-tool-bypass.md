---
id: FR-0042
title: reflect.sh --disallowedTools does not block Write tool; reflections mutate project files
status: Open
filed: 2026-05-02
source: cross-cutting synthesis 2026-05-02T03:23:48Z; reflect-sh-disallow-list-gap-2026-05-01T16-48Z.md
severity: high
---

# FR-0042 — reflect.sh Write bypass: read-only policy not enforced

## Observed behavior

The reflection job for skillfoundry-harness at 2026-05-01T14:26Z mutated
`CURRENT_STATE.md` via the `Write` tool (14:29:54Z) and via `Bash(python3 open().write())`
(14:28:34Z). The HEAD-and-dirty-tree safety net in `reflect.sh` caught this and fired
a handoff (`general-skillfoundry-harness-reflection-mutated-head-investigation-2026-05-01T14-35Z.md`).

The synthesis confirms: `Write` is still not in `reflect.sh --disallowedTools` as of
2026-05-02T03:23Z. Additionally, a git commit was triggered by an unknown host process
that scraped a `git commit -m "..."` command embedded in CURRENT_STATE.md's
"suggested next action" text.

## Why this matters

Reflections are explicitly "read-only and propose-only" per workspace rules. A reflection
that mutates project files breaks the control-plane/execution-plane separation and can
produce false git state (e.g., commit `fdbc781` attributed to a reflection session).

## Fix required

1. **Immediate**: Add `"Write"` and Bash write-equivalent patterns to `--disallowedTools`
   in `scripts/lib/reflect.sh` ~line 108.
2. **Structural**: Change CURRENT_STATE.md write path — reflection sessions should emit
   to stdout; `reflect.sh` captures and writes the file externally.
3. **Hygiene**: Stop embedding `git commit -m "..."` commands in CURRENT_STATE.md
   suggested-actions text. Replace with prose.
4. **Identify**: Find the auto-commit mechanism that scraped and executed the embedded
   command (`systemctl list-timers --all`, `crontab -l`).

## Note

This fix is Tier-C (`scripts/lib/` is read-only from tick sessions). Requires attended
executive session with operator posture.

## Related

- INBOX: `reflect-sh-disallow-list-gap-2026-05-01T16-48Z.md` (routing handoff with fix spec)
- Synthesis: `cross-cutting-2026-05-02T03-23-48Z.md` Pattern 5
- Affected commit: `fdbc781` in skillfoundry-harness repo
