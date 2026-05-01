---
id: FR-0040
title: reflect.sh disallow-list allows Write and Bash(python3) — reflection sessions can mutate project files
status: Open
created: 2026-05-01
source: runtime/.handoff/general-skillfoundry-harness-reflection-mutated-head-investigation-2026-05-01T14-35Z.md
severity: high
---

# FR-0040: reflect.sh disallow-list gap — Write + Bash(python3) bypass

## What happened

The reflection session for skillfoundry-harness at 2026-05-01T14:26Z wrote to
`CURRENT_STATE.md` via two paths that the current `--disallowedTools` does NOT block:
1. `Write` tool (entry at 14:29:54.529Z)
2. `Bash(python3 -c "…open('CURRENT_STATE.md','w').write(content)…")` at 14:28:34.923Z

The current disallow list blocks `Edit` and `NotebookEdit` but not `Write`.
It blocks specific `git`/`rm`/`docker` Bash patterns but not `python3` or other
file-writing Bash invocations.

## Wider structural problem

The disallow list is an allowlist of well-known names. Any new Bash binary that
mutates files (`tee`, `cp`, `dd`, `awk -i inplace`, `sed -i`, `perl -i`, `node`, etc.)
will bypass it. Patching individual binaries is a treadmill.

## What auto-committed the file (open question)

The `reflect.sh` post-session auto-commit should have been the sanctioned path for
CURRENT_STATE.md to land. Instead, `fdbc781` was committed at 14:28:35Z — 1 second
after the python3 write — with the exact `git commit -m` line that CURRENT_STATE.md
had embedded as a suggested command for the next agent to run. A separate auto-commit
process on the host (not in `.git/hooks/`, not in the reflection JSONL) appears to
match patterns in CURRENT_STATE.md and run them. This mechanism is unidentified.

## Recommended fixes (from investigation)

1. **Immediate**: Add `"Write"` and `"Bash(python3:*)"` to `reflect.sh` `--disallowedTools`.
   Migrate reflection report write to a post-session `tee` invocation outside the session.
2. **Structural**: Remove instruction-embedded `git commit -m "..."` lines from
   CURRENT_STATE.md templates. Suggestions that include ready-to-execute shell become
   triggers if any auto-runner is scraping them.
3. **Long-term**: Run reflection in a sandboxed `git worktree`. Any session writes
   are structurally invisible to origin. This eliminates the disallow-list treadmill.
4. Find and identify the auto-commit process running on the host between 14:28:34Z
   and 14:28:35Z. Check `systemctl list-timers --all`, `crontab -l`, and workspace
   monitoring scripts.

Fix lives in `scripts/lib/reflect.sh` (Tier-C — attended executive session required).

## References

- runtime/.handoff/general-skillfoundry-harness-reflection-mutated-head-investigation-2026-05-01T14-35Z.md
- commit fdbc781 in skillfoundry-harness repo
