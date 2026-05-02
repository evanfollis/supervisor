---
id: FR-0040
title: reflect.sh disallow-list does not block Write tool — reflections mutate project files
status: Open
created: 2026-05-01
severity: high
projects: supervisor (scripts/lib/), all reflected projects
---

# FR-0040: reflect.sh disallow-list gap — Write tool not blocked

## What happened

The `reflect.sh` script uses `--disallowedTools` to enforce read-only-and-propose-only
reflection sessions. It blocks `Edit` but NOT `Write`. Reflections actively use the
`Write` tool to update CURRENT_STATE.md — this write lands in the project working tree.

Confirmed at 2026-05-01T14:26Z: skillfoundry-harness reflection wrote to CURRENT_STATE.md
via the Write tool (14:29:54Z) and via `python3 open().write()` Bash (14:28:34Z). The
resulting commit (fdbc781) appears to have been triggered by an autocommit mechanism
that scraped a `git commit -m` command embedded in CURRENT_STATE.md's suggested actions.

## Policy contradiction

CLAUDE.md says reflections are "read-only and propose-only — never commits project code."
Operational reality: every reflection writes CURRENT_STATE.md via the Write tool. The
policy and implementation diverge. This must be resolved explicitly, not left ambiguous.

## Recommended fix

Option A (recommended): Add `Write` to `--disallowedTools`. Have `reflect.sh` itself
write CURRENT_STATE.md post-pass based on structured stdout from the reflection session.

Option B: Keep Write allowed but document it as the one sanctioned exception; restrict
to CURRENT_STATE.md only (requires runtime enforcement, not just disallow-list).

## Secondary fix

Identify the mechanism that scraped and ran a `git commit -m "..."` command from
CURRENT_STATE.md content. Candidates: autocommit cron, session hook. Check:
```bash
systemctl list-timers --all | grep -E 'autocommit|commit'
find /opt/workspace -name "*.sh" | xargs grep -l CURRENT_STATE
```

## References

- INBOX: reflect-sh-disallow-list-gap-2026-05-01T16-48Z.md
- Investigation: runtime/.handoff/general-skillfoundry-harness-reflection-mutated-head-investigation-2026-05-01T14-35Z.md
- Synthesis pattern 5: cross-cutting-2026-05-02T03-23-48Z.md
