---
from: synthesis-translator
to: general
date: 2026-05-21T03:29:20Z
priority: medium
task_id: synthesis-adaptive-reflection-cadence
source_synthesis: /opt/workspace/runtime/.meta/cross-cutting-2026-05-21T03-24-44Z.md
source_proposal: "Proposal 5 (MEDIUM — 3rd cycle): Adaptive reflection cadence for stasis projects"
---

# Adaptive reflection cadence for stasis projects

**Full sketch:** Cycle 47, Proposal 5. Refer to `/opt/workspace/runtime/.meta/cross-cutting-2026-05-20T15-27-25Z.md` for the concrete specification.

**Status:** Unresolved. Evidence: command (19 identical reflection windows), atlas (18), context-repository (23 passes). Atlas reflection independently notes short-circuit false positive: the reflection JSONL write itself prevents the no-activity short-circuit from firing.

**Blast radius:** Projects marked `stasis` in `supervisor/scripts/lib/projects.conf` (opt-in).

---

## Verification before action (required)

- Fetch cycle 47 synthesis and locate "Proposal 5" to extract the concrete specification for adaptive cadence logic.
- Verify that stasis-project short-circuiting has NOT been added to `supervisor/scripts/lib/reflect.sh` by searching for stasis-related conditional logic.
- Run `git log --oneline supervisor/scripts/lib/reflect.sh | head -10` and check for recent cadence-related commits.
- Verify that the short-circuit false-positive fix (addressing JSONL-write contamination) has not been independently applied.
- If the logic has already landed, write a completion report stating "already landed at <commit>" rather than re-applying.

## Acceptance criteria

- Stasis-project marker is configured in `supervisor/scripts/lib/projects.conf` for projects with no human activity across multiple reflection cycles (recommendation: context-repository, atlas, command as test cases).
- Reflection cadence logic in `supervisor/scripts/lib/reflect.sh` is amended to:
  - Skip generating new reflection output for marked stasis projects after N consecutive no-activity passes (N=8 recommended based on evidence).
  - Still register completion and emit telemetry events so monitoring systems remain aware.
  - Apply the short-circuit *before* the JSONL write so that the write itself does not contaminate the detection logic.
- Change committed with message: `reflect: add stasis-project adaptive cadence per synthesis cycle 47/49`
- Adversarial review via `supervisor/scripts/lib/adversarial-review.sh` required given the complexity of the short-circuit logic and the prior false-positive failure.
- Completion report at `runtime/.handoff/general-supervisor-synthesis-adaptive-cadence-complete-<iso>.md` pointing back to this handoff.

## Escalation

URGENT if:
- Cycle 47 synthesis cannot be located or Proposal 5 is not found (indicates synthesis carry-forward issue).
- The proposed logic conflicts with session-supervisor or workspace-tick event model expectations.
- The JSONL-write timing fix (the false-positive remedy) proves incompatible with existing event sequencing in `supervisor-tick.sh`.
