---
id: FR-0035
title: Tick's verify-state.sh called before dirty-tree gate — caused self-blocking
status: resolved
filed: 2026-04-20
resolved: 2026-04-20
resolution: Fixed in commit 5618ef1 — moved verify-state.sh call to after dirty-tree check
---

# FR-0035 — Tick verify-state.sh ordering

## What happened

`supervisor-tick.sh` called `verify-state.sh` at the top of every run, before the
dirty-tree safety check. `verify-state.sh` runs a Claude Code headless session that
regenerates `system/verified-state.md`. That session left the working tree dirty,
which caused the tick's own dirty-tree gate to abort immediately on every subsequent
run. Result: 9+ consecutive tick skips with reason "dirty tree" until the attended
session diagnosed and fixed it.

## Root cause

Ordering assumption: `verify-state.sh` was assumed to be read-only. In practice it
writes `system/verified-state.md`, making the tree dirty.

## Fix

Commit `5618ef1` (2026-04-20T12:24Z) reordered the verify-state call to after the
dirty-tree gate, so tree cleanliness is checked before anything writes to it.

## Status: Resolved
