# Proposal — Wire adversarial-review.sh into tick prompt

**From**: supervisor tick 2026-04-17T22-48-12Z
**Source**: cross-cutting synthesis 2026-04-17T15:23Z, Proposal 1
**Type**: Playbook amendment (`supervisor-project-tick-prompt.md`)
**Status**: proposed — attended session must review before applying

## Problem

The `adversarial-review.sh` workaround for the `/review` EROFS blocker is
available and validated (atlas ingest review ran cleanly via `codex exec
--sandbox read-only`). However, tick sessions don't know about it because the
tick prompt doesn't reference it. Every substantial commit from tick sessions
this cycle shipped without adversarial review. This is a routing gap, not a
capability gap.

**Evidence**: command `e234231` (533 additions, 7 files), atlas `5c3a5ff`
(slug cutover changing evidence pipeline ID contract), and the preflight
landing page (`8e9bf50`, 139 insertions) all shipped without review.

## Proposed delta

Add after the completion-report section in `supervisor-project-tick-prompt.md`:

```
**Adversarial review gate**: If this tick produced commits touching ≥3 files
or ≥100 net lines, run `adversarial-review.sh <changed-files-or-summary>` 
before writing the completion report. Include the review artifact path in the
completion report under an `## Adversarial review` section. If the review 
identifies a real failure mode, fix it before closing the tick. If review is 
blocked (Codex unavailable, timeout), note the blocker explicitly — do not 
skip silently.
```

## Rationale

- The capability exists (`scripts/lib/adversarial-review.sh`).
- Codex path is validated in production (atlas review, 2026-04-17).
- `/review` EROFS blocker is the only reason this wasn't wired in earlier.
- Tick sessions ship the most code autonomously; they have the highest leverage
  from adversarial review and the least current enforcement.

## Blast radius

All project tick sessions. Review runs in Codex read-only sandbox — cannot
modify project state. Cost: one Codex call per non-trivial tick.

## Acceptance criteria

- `supervisor-project-tick-prompt.md` updated with the gate text above.
- Next non-trivial tick includes `## Adversarial review` in its completion report.
- FR-0025 updated with "tick prompt gate landed."

## Notes for attended session

1. The exact wording can be adjusted — the key invariant is that any tick
   touching ≥3 files must run adversarial review and include the artifact path.
2. The `adversarial-review.sh` script takes a file path or a text description;
   for a tick, passing the CURRENT_STATE or the commit diff summary is sufficient.
3. This is a Tier B surface (playbook) — do not edit `supervisor-project-tick-prompt.md`
   without attended review. Write the amendment; then commit on main.
