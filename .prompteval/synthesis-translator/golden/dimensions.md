# synthesis-translator golden set — dimensions

Axes of variation for the input space (a cross-cutting synthesis file):

| Dimension | Values covered |
|---|---|
| proposal_count | 0, 1, 2, 3 |
| target_scope | supervisor file → INBOX; project file → HANDOFF_DIR; CLAUDE.md/charter → INBOX |
| bucket | autonomous; principal-money; principal-named-person; ambiguous (principal-authorization note on an otherwise-automatable change) |
| distractors | "Questions for the human" section; standing-recommendations table; none |
| mode | normal; short-circuit banner (`# Synthesis skipped —`) |
| perturbation | clean; unicode/backticks in titles; proposals sharing a root cause (no batching allowed) |

Strata deliberately excluded in v1 (recorded in spec.json known_gaps):
idempotency collision (pre-existing handoff files in target dirs).

Learned live (baseline run 20260712T011927Z): the eval sandbox retains
read access to the real workspace, and the model performs the prompt's
primary-verification duty unprompted — a case whose proposal contradicts
live file content is (correctly) skipped as stale. Consequences: (1) the
stale-state stratum IS coverable and now has a case; (2) emit-path cases
must reference real paths with claims consistent with reality — additive
changes are the safe construction.

Provenance: cases built from real synthesis files (C138 excerpts) are
`production`; constructed edge cases are `synthetic`. Expected outcomes
were hand-audited 2026-07-12 against the prompt's own rules and the
people-or-money rubric (ADR-0020 refinement).
