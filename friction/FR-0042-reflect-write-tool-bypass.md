---
name: FR-0042-reflect-write-tool-bypass
description: reflect.sh --disallowedTools does not block Write tool; reflections write CURRENT_STATE.md to project repos in violation of "read-only and propose-only" policy
type: friction
status: Open
created: 2026-05-02
---

# FR-0042 — reflect.sh Write tool bypass

## What happened

The workspace CLAUDE.md states: "Read-only and propose-only — never commits project code." The `reflect.sh` script enforces this via `--disallowedTools`. But the list includes only `Edit`, not `Write`. Every reflection session writes `CURRENT_STATE.md` directly to the project working tree via the `Write` tool.

Confirmed incident: skillfoundry-harness reflection at 2026-05-01T14:26Z wrote `CURRENT_STATE.md` via `Write` tool. An auto-commit mechanism then detected the dirty tree and committed it (`fdbc781`). The commit was not authorized by the reflection job; it was a side-effect.

## Evidence

- INBOX: `supervisor/handoffs/INBOX/reflect-sh-disallow-list-gap-2026-05-01T16-48Z.md`
- INBOX: Multiple `proposal-reflect-write-bypass-*` entries (2026-05-02)
- Synthesis Pattern 4 (multiple cycles): three projects with uncommitted CURRENT_STATE drift

## Failure class

Policy contradiction: the charter says read-only, the tooling allows writes. The contradiction is resolved by the tooling (writes happen) not the charter (reads only). Three projects have CURRENT_STATE.md drift as a result.

## Fix required (Tier C — scripts/lib/)

Add `"Write"` to `--disallowedTools` in `reflect.sh` (~line 112). Then establish a post-reflection step in `reflect.sh` itself to update CURRENT_STATE.md from the reflection output and commit it.

See: `handoffs/INBOX/reflect-sh-disallow-list-gap-2026-05-01T16-48Z.md` for the exact fix.

## Status: Open — operator session required to edit scripts/lib/
