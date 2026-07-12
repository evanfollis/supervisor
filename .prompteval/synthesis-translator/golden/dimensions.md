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

Learned live (baseline runs 1–5, 2026-07-12): this prompt is **stateful**
— the adapter runs with cwd=/opt/workspace (matching production), the
model reads the live workspace, and correct behavior depends on live
state. Five of the first twelve authored cases encoded wrong expected
outcomes; in every disagreement the model's primary verification was
right and the case author was wrong:

- fictional patch target → correctly skipped as stale (run 1)
- premise already fixed by synaplex@2a262b1 → correctly skipped (run 2)
- wrong file paths → correctly refused, unverifiable (runs 3–4)
- patch referencing an undefined variable → correctly refused as
  would-break-the-script (run 5)
- already-archived handoffs → correctly skipped as landed (run 5)
- real C138 P7 proposal conflicting with ADR-0037 exposed inconsistent
  decision discovery: one run caught the conflict and later runs did not.
  The prompt now requires an identifier-based decision search before every
  workspace-charter or architecture handoff; the case expects zero emission
- reflect failure telemetry proposal became an already-landed/stale case
  after telemetry landed in `reflect.sh`; it now expects skip-with-reason
  rather than duplicate handoff emission
- the generic charter-routing case deliberately avoids `LATEST_SYNTHESIS`,
  reserving that exact proposal for the ADR-0037 conflict regression case

Construction rules that survive: emit-path cases use additive,
self-contained proposals on verified-real paths; skip-path cases are
state-independent (principal-scope, format) or verified-true-at-authoring
(stale, conflict). The prompt itself was strengthened once (mandatory
verification) after run 2 showed verification was inconsistent — the one
genuine prompt defect found so far.

Provenance: cases built from real synthesis files (C138 excerpts) are
`production`; constructed edge cases are `synthetic`. Expected outcomes
were hand-audited 2026-07-12 against the prompt's own rules and the
people-or-money rubric (ADR-0020 refinement).
