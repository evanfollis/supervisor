---
from: synthesis-translator
to: general
date: 2026-05-23T03:28:48Z
priority: high
task_id: synthesis-cadence-stasis
source_synthesis: /opt/workspace/runtime/.meta/cross-cutting-2026-05-23T03-23-38Z.md
source_proposal: Proposal 2 (NEW) — Reduce reflection/synthesis cadence for stasis projects and the synthesis loop itself
---

# Reduce reflection/synthesis cadence for stasis projects

## Proposal body

**Type:** Shared primitive change + `projects.conf` amendment.

**What:** 
(a) Add `cadence=stasis` support to `reflect.sh` / `projects.conf`. Projects with zero commits in 3+ consecutive windows reflect once per 24h instead of 12h. Synaplex (13th skip), context-repository, and command are candidates. 
(b) Consider reducing synthesis cadence from 12h to 24h until the execution-side disconnect (Pattern 2) is addressed.

**Rationale:** This is the 8th cycle producing a correct diagnosis that is not consumed. The reflections themselves are asking for cadence reduction — researcher says it is "not adding diagnostic value beyond counter increment," harness reached "ceiling" on its escalations, command proposed reducing its own cadence. Eight correct diagnoses of a 1-line bug is not analysis working harder; it is analysis running on autopilot.

**Blast radius:** Stasis-tagged projects (opt-in via `projects.conf`). Synthesis cadence change is automatic but easily reversible.

## Verification before action (required)

- Check git log for recent cadence-related changes: `git log --oneline -20 | grep -i cadence`
- Read `scripts/lib/projects.conf` to see current format
- Read `scripts/lib/reflect.sh` to understand how it iterates projects
- Verify that zero commits in 3+ consecutive windows is a distinguishing metric (check reflect job invocation cadence in systemd units)

## Acceptance criteria

- `projects.conf` supports optional `cadence=stasis` tag (e.g., `synaplex|/opt/workspace/projects/synaplex|reflect-prompt.md|cadence=stasis`)
- `reflect.sh` reads the cadence tag and skips projects tagged `stasis` when the 12h window fires, allowing them to be picked up only by the 24h window
- `synthesize.sh` (or a related timer) has a 24h cadence option; (b) is a judgment call — document the decision in a completion note whether you reduce synthesis cadence or defer it as a follow-up
- Change committed with clear message explaining the synthesis observation
- Adversarial review via `supervisor/scripts/lib/adversarial-review.sh` for the multi-file changes
- Completion report at `runtime/.handoff/general-synthesis-cadence-stasis-complete-<iso>.md`

## Escalation

URGENT if:
- The synthesis observation is already addressed by a more recent change you find in git history
- The cadence-control mechanism is more complex than expected (e.g., timers are in systemd, not script-conditional)
- The synthesis recommends a judgment call (reduce synthesis cadence to 24h) without principal input — flag whether this is autonomous or requires a decision

