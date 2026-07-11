---
from: synthesis-translator
to: general
date: 2026-05-21T15:29:16Z
priority: medium
task_id: synthesis-adaptive-reflection-cadence
source_synthesis: /opt/workspace/runtime/.meta/cross-cutting-2026-05-21T15-24-47Z.md
source_proposal: "Proposal 5 (MEDIUM — 4th cycle): Adaptive reflection cadence for stasis projects"
---

# Adaptive reflection cadence for stasis projects

**Type:** Shared primitive change.

**Change:** Add `cadence=stasis` to `projects.conf` that skips reflection when zero commits in Nh window. Atlas reflection notes the short-circuit logic has a false positive (reflection's own JSONL write prevents the short-circuit from firing).

**Blast radius:** Projects marked `cadence=stasis` in `projects.conf` (opt-in).

## Context

Several projects in the reflection loop are in extended idle periods with zero commits:
- **context-repository**: 24 idle reflection passes, 10 days since last commit
- **synaplex**: 10th consecutive reflection skip
- **skillfoundry-* projects**: multiple skipped passes

Reflecting on projects with zero activity still consumes computation and generates reflection session artifacts. The synthesis proposes an optimization: if a project has zero commits in a configurable window (e.g., 12h, 24h, 72h), mark it with `cadence=stasis` and skip reflection until it becomes active again.

## Current reflection behavior

All projects in `projects.conf` are reflected on every 12h cycle, regardless of activity. The reflection loop generates a JSONL transcript, reads git history, verifies state, and writes findings even for projects with zero commits.

## Proposed behavior

1. Add an optional `cadence` field to `projects.conf` entries (format: `<name>|<path>|<prompt-template>|<cadence>`).
2. For entries with `cadence=stasis`, the reflection job checks: has this project had any commits in the last Nh? (recommend: 12h, or customize per project).
3. If no commits, skip the reflection entirely; record a `skipped_cadence_stasis` event in supervisor-events.jsonl.
4. When a stasis-mode project gets a commit, the next cycle's reflection will fire normally.

## Known issue from atlas reflection

The atlas reflection notes that the proposed short-circuit has a false positive: the reflection job's own JSONL write at session end prevents the short-circuit from correctly detecting "zero commits." The fix is to check for non-reflection commits explicitly (e.g., exclude JSONL writes, exclude session-summary artifacts).

## Verification before action (required)

- Run `git log --oneline -20` on `/opt/workspace/supervisor`. Check if this change has already landed.
- Read `/opt/workspace/supervisor/scripts/lib/projects.conf`. Check if the `cadence` field exists.
- Read `/opt/workspace/supervisor/scripts/lib/reflect.sh` or the reflection job script. Check if stasis-cadence logic is implemented.
- If any is true, write a completion report stating "already landed" rather than re-applying.

## Acceptance criteria

- `projects.conf` entries can now have an optional 4th field: `cadence`.
- Default cadence (when unspecified) remains the current 12h cycle.
- Entries with `cadence=stasis` are skipped if the project has zero commits in the last 12h (configurable per entry or globally).
- The commit-detection logic explicitly excludes reflection artifacts (JSONL session transcripts, auto-generated files) so it correctly identifies "zero real commits."
- A `skipped_cadence_stasis` event is emitted to supervisor-events.jsonl when a stasis-mode project is skipped.
- Projects transition out of stasis automatically when a real commit lands.
- Change committed with message explaining the adaptive cadence (synthesis cycle reference).
- Completion report at `runtime/.handoff/general-supervisor-synthesis-adaptive-cadence-complete-<iso>.md`.

## Escalation

URGENT if:
- The reflection job errors when parsing the new 4-field format from projects.conf — ensure backwards-compatibility for existing 3-field entries.
- The commit-detection logic is too loose/tight and either skips active projects or fires on stasis projects — adjust the exclusion patterns.
- Stasis mode is configured but projects never transition back out — check the reactivation logic.
