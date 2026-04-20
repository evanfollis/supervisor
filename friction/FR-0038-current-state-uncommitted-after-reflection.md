---
id: FR-0038
title: CURRENT_STATE.md uncommitted after reflection — M4 hook loads stale version
status: open
filed: 2026-04-20
---

# FR-0038 — CURRENT_STATE.md uncommitted after reflection

## What happened

`reflect.sh` runs with `--disallowedTools` preventing commits. After the reflection
session updates `CURRENT_STATE.md`, the file sits as an unstaged working tree change.
It remains there for 24-48h until an attended session commits it — or until `git checkout`
discards it during the next tick's dirty-tree check.

The M4 hook (`session-start-context-load.sh`) auto-injects the committed version of
`CURRENT_STATE.md`. If the committed version is stale, every session start loads stale
context and agents make decisions based on it.

## Observed impact

- Atlas reflection documented CURRENT_STATE.md claiming "branch is 2 ahead of origin/main"
  when the branch was already clean and pushed. The stale committed file would mislead
  any session starting cold.
- 4 projects affected per the 15:28Z synthesis (atlas, harness, valuation, context-repo).

## Proposed fix (Proposal 2 from cross-cutting-2026-04-20T15-28-05Z)

In `reflect.sh`, after the Claude/Codex session exits, add:

```bash
cd "$PROJECT_DIR"
if ! git diff --quiet -- CURRENT_STATE.md 2>/dev/null; then
  git add CURRENT_STATE.md
  git commit -m "reflection: update CURRENT_STATE.md $(date -u +%Y-%m-%dT%H:%M:%SZ)"
fi
```

This is within supervisor authority (`reflect.sh` is workspace infrastructure). Requires
attended `scripts/lib/` edit (Tier C for direct edit; propose via INBOX per charter).

## Status: Open
