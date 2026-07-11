---
from: synthesis-translator
to: general
date: 2026-05-22T15:30:16Z
priority: medium
task_id: synthesis-adaptive-reflection-cadence
source_synthesis: /opt/workspace/runtime/.meta/cross-cutting-2026-05-22T15-24-17Z.md
source_proposal: Proposal 4 (MEDIUM — 5th cycle)
---

# Adaptive reflection cadence for stasis projects

## Summary

Projects with zero commits in N consecutive 12h reflection windows are producing reflection output that exceeds signal value. Synaplex has been skipped 12 consecutive cycles; context-repository and command have not been touched in 5+ and 10+ cycles respectively. The reflection job itself (reflect.sh) is working correctly, but the insights it produces are primarily counter-increments rather than diagnostic value.

The reflections themselves are asking for this: Synaplex proposed reducing its own cadence; researcher notes cycles are "not adding diagnostic value beyond counter increment." This is a self-policing signal.

## The change

Add an optional `cadence` field to `supervisor/scripts/lib/projects.conf` to support stasis projects. Format:

```
# Projects to include in the 12h reflection loop.
# Format: <name>|<path>|<optional-prompt-template>|<optional-cadence>
# Cadence: 12h (default) or stasis (once per 24h)
#
# Name is used in output file naming and telemetry filtering.
# Path must be an absolute directory (typically a git repo).
# Prompt template is optional; defaults to reflect-prompt.md.
# Cadence is optional; defaults to 12h. stasis projects reflect once per 24h.

# Products
atlas|/opt/workspace/projects/atlas|||12h
skillfoundry-harness|/opt/workspace/projects/skillfoundry/skillfoundry-harness|||12h
skillfoundry-valuation|/opt/workspace/projects/skillfoundry/skillfoundry-valuation-context|||12h
skillfoundry-researcher|/opt/workspace/projects/skillfoundry/skillfoundry-researcher-context|||12h

# System
command|/opt/workspace/projects/command|||stasis
context-repository|/opt/workspace/projects/context-repository|||stasis
supervisor|/opt/workspace/supervisor|reflect-supervisor-prompt.md|12h
synaplex|/opt/workspace/projects/synaplex|||stasis
```

Then update `reflect.sh` (or the calling job) to respect the cadence field and skip stasis projects on the 12h odd cycles (only reflect on 24h boundaries).

## Implementation approach

Two options (choose one):

**Option A (simpler):** Modify `reflect.sh` to skip stasis projects when the hour component of the current time is an odd hour (i.e., only reflect stasis projects at 02:xx and 14:xx UTC, not at every 12h cycle).

**Option B (more explicit):** Add a `reflect.sh --cadence stasis` mode that skips projects unless their last reflection is >24h old. Requires tracking per-project last-reflection timestamp.

Option A is recommended: lower code complexity, and the UTC hour offset is already baked into the cron schedule (02:17 and 14:17 UTC).

## Impact

- Affected: `projects.conf` and `reflect.sh` (or the supervisor job that calls it)
- Blast radius: Stasis projects only (synaplex, context-repo, command). Active projects continue 12h cadence.
- Side effect: Reduces telemetry volume and job overhead for projects with no commits. Diagnostic record is still created on each 24h cycle, so trend data is preserved.

## Verification before action

- Run `git log --oneline -20` on `supervisor/`. Confirm no recent commit touches `projects.conf` or reflection scripts.
- Read `supervisor/scripts/lib/projects.conf` and confirm no `cadence=` field exists.
- Count lines: projects.conf should have 8 active lines (4 products + 4 system). If it has more, check what's been added.
- If all confirmed, proceed.

## Acceptance criteria

- `projects.conf` is extended to support an optional cadence field (default 12h, optional stasis).
- Stasis projects are marked in `projects.conf`: synaplex, context-repository, command.
- Reflection scheduling logic respects the cadence: stasis projects are skipped on odd 12h cycles.
- First stasis reflection run confirms the skip happens (check `runtime/.meta/*-reflection-*.md` to see skipped entries).
- Commit message (imperative): "Add adaptive reflection cadence — mark stasis projects for 24h-only reflection"
- Adversarial review: optional (straightforward config change, but review adds confidence that the cadence choice is correct).

## Escalation

URGENT if:
- After first run, a stasis project suddenly produces commits (no longer in stasis). Update `projects.conf` immediately to re-enable 12h cadence.
- The stasis skip logic creates a false negative in diagnosis (i.e., a problem in a stasis project goes unreported for >24h when early detection would have mattered). If this happens, adjust the cadence threshold and escalate.
