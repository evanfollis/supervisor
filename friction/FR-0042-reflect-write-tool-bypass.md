---
id: FR-0042
slug: reflect-write-tool-bypass
status: open
created: 2026-05-02
discovered-by: supervisor-tick-2026-05-01T16-48-26Z
---

# FR-0042: reflect.sh --disallowedTools does not block Write; reflections mutate project files

## Symptom

The reflection session for skillfoundry-harness at 2026-05-01T14:26Z mutated
`CURRENT_STATE.md` via the Write tool despite `reflect.sh` specifying
`--disallowedTools`. `Write` was not in the disallow list; only `Edit` was.
The mutated CURRENT_STATE.md contained a `git commit -m "..."` command in
its "suggested next action" field which was subsequently executed by an
unknown host process, resulting in an unauthorized commit (`fdbc781`).

## Impact

Reflection sessions can silently mutate project working trees. CURRENT_STATE.md
across multiple projects has uncommitted reflection-job content. One commit
was triggered without human review. The workspace rule "read-only and
propose-only" is violated every reflection cycle.

## Fix required

Add `"Write"` to `--disallowedTools` in `scripts/lib/reflect.sh` line ~108.
CURRENT_STATE.md updates should be written by `reflect.sh` post-session from
the reflection output, not by the session itself. See
`handoffs/INBOX/reflect-sh-disallow-list-gap-2026-05-01T16-48Z.md` for
exact patch with two options (A: output-file flag, B: stdout capture).
