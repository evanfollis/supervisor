---
id: FR-0041
slug: synthesis-execution-gap
status: open
created: 2026-05-02
discovered-by: cross-cutting-synthesis-2026-05-02T15-27-50Z
---

# FR-0041: 11 synthesis cycles produced 0 implemented proposals

## Symptom

The workspace cross-cutting synthesis loop has now run for 11 consecutive
12h windows (starting ~Apr 25). Each cycle produces 3-5 proposals. Total
proposals generated: ~40+. Total proposals implemented: 0.

## Impact

The synthesis loop is functioning as a diagnostic archive rather than a
work queue. API cost accumulates for synthesis runs that produce no changes
to the workspace. Structural issues identified by reflection (ghost-writes,
reflect.sh bypass, atlas frozen state) persist indefinitely despite being
named and escalated correctly.

## Root cause

Three dispatch paths exist:
(a) Principal-attended sessions — have not activated across this window
(b) Autonomous tick sessions — limited to Tier-A/B writes; cannot edit
    `scripts/lib/`, CLAUDE.md, or existing decisions
(c) Handoff-to-general-session pipeline — marks handoffs `.done` without
    applying the requested changes (tick context is same as (b))

Proposals require changes to Tier-C surfaces (scripts/lib/reflect.sh,
scripts/lib/synthesize.sh, CLAUDE.md). Without principal presence or
expanded tick authority for infrastructure changes, they cannot land.

## Resolution path

Either: (A) Principal triage session to implement the backlog, or (B) a
decision granting tick sessions Tier-B-auto authority for workspace
infrastructure changes meeting specific criteria. See synthesis Proposal 5
(`proposal-tier-b-auto-authority-2026-05-02T18-50Z.md`) and the synthesis
Questions for the human section.
