---
id: FR-0039
title: FR numbering collision across unmerged tick branches
status: Open
created: 2026-04-25T20:48Z
source: supervisor-tick-2026-04-25T20-48-43Z
---

# FR-0039 — FR numbering collision across unmerged tick branches

## Observed

Three tick branches each independently incremented the FR counter from the same base on `main`:

- `ticks/2026-04-20-22` wrote FR-0035 through FR-0038 (current-state-uncommitted, tick-verify-state, inbox-circular-dependency, fr-candidate-backlog)
- `ticks/2026-04-25-18` wrote FR-0038 (synthesis-job-writing-empty-stubs)

FR-0038 now names two different friction records on two different branches. Neither is visible from `main`. Main's highest FR is FR-0037.

This collision was anticipated in the 18:47 tick's FR-0038 body ("attended session must renumber one") but the underlying structural cause — tick branches accumulating without merging — was not addressed.

## Root cause

Tick branches write Tier-A content (friction records, active-issues) on a branch, commit them, but are never merged back to `main`. Each subsequent tick branches from `main`, sees the same highest FR number (FR-0037), and uses FR-0038 independently. The collision is an inevitable consequence of the merge gap.

## Downstream damage

1. FR records from the aged tick branch are invisible from `main` — sessions on main are blind to captured friction.
2. When the aged branch is eventually merged, attended session must renumber to resolve collisions before merge.
3. The friction surface underreports: current main shows 37 FRs but at least 4 additional (FR-0035–0038 variants) exist unreleased.

## Resolution needed

1. Attended session merges or rebases `ticks/2026-04-20-22` and `ticks/2026-04-25-16` / `ticks/2026-04-25-18` into main.
2. Resolve FR-0038 collision: pick one definition, renumber the other to FR-0039 (or whichever is next available after merge).
3. Structural fix: tick branches should not accumulate. Either (a) tick commits directly to main, or (b) a fast-forward merge of the tick branch is an automated step before the next tick.
