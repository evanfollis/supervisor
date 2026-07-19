# ADR-0039: Prompt evaluation loops — every prompt versioned, golden-set gated

Date: 2026-07-12
Status: accepted (adversarial review by Codex 2026-07-12; all 3 blockers +
6 majors + 1 minor addressed before acceptance — see §Adversarial review)

## Context

Principal directive (2026-07-12, attended session, verbatim intent): every
prompt that runs in the system must have an evaluation loop wired into it.
At minimum: an LLM-generated golden set of inputs + output criteria and an
appropriate grader; every prompt versioned and gated through CI; edits to
prompts must pass through CI; as real interactions accumulate, they replace
the LLM-generated golden set; golden sets stay current as the system
evolves; the same loops feed prompt optimization. "Because this will become
so foundational, it MUST be built of the highest quality."

Inventory (2026-07-12): the workspace had ~2 SDK system prompts (synaplex
`intake/score.py`, `intake/synthesize.py`), ~4 TS prompt builders (command
`review.ts`, `executor.ts`, `threadConversation.ts`, `metaLearning.ts`),
9 externalized `*-prompt.md` files + 5 `SKILL.md` files (supervisor), and
agent-charter markdown (atlas `CLAUDE.md`, skillfoundry `mission.md` +
profiles). No golden sets, no graders, no prompt registry, no eval CI
exists anywhere. Prompts are versioned only implicitly by git. The shared
deploy gate is `supervisor/scripts/lib/preflight-deploy.sh` (push →
webhook → autodeploy path); no repo uses GitHub Actions.

External state of practice (researched 2026-07-12; primary sources:
Anthropic "Demystifying evals for AI agents" 2026-01-09, Anthropic
statistics-of-evals 2024-11, OpenAI evaluation flywheel cookbook 2025-10,
Hamel Husain/Shreya Shankar evals FAQ 2026-01, Braintrust eval lessons
2025-07):

- Start with 20–50 cases drawn from real failures; error analysis before
  infrastructure; grow toward hundreds.
- Grader hierarchy: deterministic/code graders first; LLM-judge only for
  genuinely subjective dimensions; humans calibrate, they don't grade in
  the loop.
- Binary pass/fail per named failure mode beats Likert averages for
  gating. Judges: reason-then-verdict, structured rubric per dimension,
  "unknown" escape hatch, low temperature, order randomization for
  pairwise, cross-model check where self-preference bias matters, and a
  human-labeled alignment set (report TPR/TNR) with periodic
  recalibration.
- Synthetic test data is generated from explicit dimension tuples in two
  steps (combinations → rendered inputs), human-audited, and labeled
  synthetic forever; it is a bootstrap, not a destination. Production
  traces continuously feed the golden set (one-way valve: production
  failure → regression case).
- CI gates on a curated regression set with response caching; multiple
  trials for stochastic tasks (pass@k for capability, pass^k for
  consistency); paired per-case comparison against baseline, not
  independent run averages.
- Prompt versions are immutable (prompt text + model + params bundled,
  content-hashed), with eval results attached to the version that earned
  promotion.
- Any optimization loop (manual or GEPA/DSPy-style) needs train/validation
  discipline plus a sealed holdout never used during iteration, or the
  eval stops measuring anything. OpenAI is shutting down its hosted Evals
  platform 2026-11-30 — own the harness in-repo; hosted platforms are
  replaceable viewers. This matches our "substrate is the stable layer"
  doctrine.

Workspace constraints that bind the design:

- **ADR-0036**: no metered API keys. All LLM execution (target prompts
  under eval, judges, synthetic-case generation) runs through the
  subscription CLIs (`claude -p`, `codex exec`).
- **Executive boundary**: the executive builds workspace infrastructure
  (`supervisor/`) but does not edit project code. Adoption inside project
  repos is project-session work, dispatched via handoffs.
- **S1-P3**: one ID-generation contract per store. All prompt/case/run IDs
  come from one hashing helper.
- **ADR-0029**: every layer emits typed telemetry events; validation is
  woven, not terminal.

## Decision

Adopt a workspace-wide **prompt-eval contract**, implemented as a shared
harness (`prompteval`), a scaffolding skill (`create-eval-loop`), and a
deploy-gate extension. The contract:

### 1. Prompt artifacts and versioning

- A **prompt artifact** is the triple (prompt text, model, params). Its
  **version** is `pv-<sha256[:16]>` of the canonicalized triple, minted by
  one helper (`prompteval.core.artifact_hash`). Versions are immutable;
  any edit mints a new version.
- Git remains the source of truth for prompt text. Prompts do **not** have
  to move out of code to be governed: a registry entry carries a **source
  pointer** (file path + extraction anchor — whole-file, delimited region,
  Python string constant, or TS template literal) and the harness extracts
  the live text at check time. Hash drift between live text and the last
  evaluated version is what the gate detects.
- Registry lives in-repo at `<repo>/.prompteval/<prompt-id>/`:
  `spec.json` (source pointer, executor config, model, params, owner,
  gate thresholds), `golden/cases.jsonl` + `golden/holdout.jsonl`
  (sealed tier, separate file), `baseline.json`, `judge/alignment.jsonl`
  (human labels for judge accountability). Run artifacts (bulky) go to
  `/opt/workspace/runtime/prompteval/<project-key>/<prompt-id>/`, never
  committed.
- A baseline binds **three hashes**: the prompt version (`pv-`), a
  **spec hash** (`sh-` — source pointer, executor config including the
  content of adapter files, judge and gate config), and a **golden-set
  hash** (`gh-` — case ids, checks, statuses, must_pass, provenance,
  gate config). The gate verifies all three against live state, so none
  of: editing the prompt, repointing the source, swapping the
  executor/adapter, or weakening the criteria can silently retain an old
  accepted baseline. Criteria edits are therefore always visible as a
  fresh run plus a reviewable diff, and remain subject to the standing
  /review-compliance gate like any code change.

### 2. Golden sets

- JSONL cases: `{id, input, checks[], provenance, status, created,
  last_validated, source, notes}`.
- `provenance` ∈ `synthetic | production | human`. Synthetic cases are
  labeled synthetic forever. `status` ∈ `active | candidate | holdout |
  smoke | retired`.
- New loops bootstrap with **12–50 cases**: synthetic generation uses
  dimension-tuple two-step (enumerate axes of variation → render inputs),
  seeded from real logged inputs whenever any exist (synaplex scored
  JSONL, runtime/.meta reflections, session transcripts). Every synthetic
  case is audited by a session (human or agent applying the skill's audit
  checklist) before activation.
- **Flywheel (one-way valve):** capture adapters sample real interactions
  into `golden/candidates.jsonl`; `prompteval promote` moves curated
  candidates to `active` (dedup by input hash, stratification check).
  Every production failure becomes a regression case. Synthetic cases
  retire as production cases cover their stratum; the harness reports the
  synthetic:production ratio so phase-out is visible, with a standing
  expectation that mature loops trend production-majority.
- **Freshness:** cases carry `last_validated`; the harness flags cases
  stale (>90d unvalidated), saturated (long all-pass streaks → rotate to
  `smoke` or retire), synthetic-majority on mature loops, and **candidate
  backlog** (≥10 unpromoted candidates or oldest >30d — a flywheel that
  captures but never promotes is stalled, and that surfaces with the same
  weight as staleness).
  Golden sets are living artifacts with the owning project as named owner;
  the reflection loop reads prompteval status files, so decay surfaces in
  the existing 12h synthesis, not a new parallel loop.

### 3. Graders

- Grader stack per case, in order: **deterministic checks first**
  (json_schema, exact, contains, regex, numeric_band, length_band,
  jsonpath field checks, custom project grader function), then **binary
  LLM-judge checks**, one rubric per named failure mode — never a single
  mega-rubric, never Likert-average gating.
- Judge protocol: reason-then-verdict, structured JSON verdict
  (`pass | fail | unknown`), escape hatch mandatory, judge model
  configured per prompt and defaulting to a **different model tier than
  the target** (and `codex exec` available as a cross-family judge where
  self-preference bias matters). `unknown` verdicts never count as pass;
  above a threshold they fail the run as "judge cannot grade this" —
  which is itself signal the rubric or case is bad.
- Judges that gate anything accumulate a human-labeled **alignment set**
  (`judge/alignment.jsonl`, starting the first time a human disputes a
  verdict); `prompteval align` re-runs the judge against those labels and
  reports TPR/TNR, failing below 0.8 — a judge that can't clear the bar
  gets its rubric revised before it gates again. Judges that gate set
  `judge.trials: 3` (majority vote) to absorb single-call noise.
- All LLM execution via subscription CLIs per ADR-0036. Provider-capacity
  failures route across subscription families first: Claude-primary calls
  try Codex next, and Codex-primary calls try Claude next. Eval runs emit
  `eventType: "throttled"` (not `failure`) and are treated as not-run only
  when both subscription providers are blocked.

### 4. CI gate

- CI in this workspace **is** the deploy gate. `preflight-deploy.sh`
  runs `prompteval check` (pure-local, no LLM calls, <1s) for **every**
  repo, fail-closed: a repo with no `.prompteval/` registry is scanned,
  and likely prompt artifacts block deploy until governed or listed as
  `not-a-prompt` with a reason. For registered prompts the gate verifies
  all three baseline hashes (§1), golden-set structural validity, holdout
  discipline, and inventory↔spec mapping (a `governed` inventory entry
  must map to a real spec sourcing that exact file). Editing a governed
  prompt without a fresh passing `prompteval run --no-cache
  --update-baseline` blocks deploy.
- Baseline acceptance requires **fresh outputs**: `--update-baseline`
  refuses cache-enabled runs unless `--allow-cached-baseline` is passed
  explicitly (and that override is recorded in the baseline). The cache
  (keyed on prompt version + spec hash + case + trial) exists for cheap
  iteration, not for acceptance.
- `prompteval run` is the LLM-expensive step, invoked by the editing
  session (the skill instructs this) — not by the deploy webhook, so the
  gate stays deterministic and fast. Runs execute N trials per stochastic
  case (default 1 for deterministic-graded prompts, 3 where judges gate),
  gate on **pass^k for must-pass cases** and **paired must-pass regression
  vs baseline** (a required case that passed at baseline and fails now
  blocks), plus a must-pass aggregate floor. The all-case aggregate is
  retained as an observational quality signal, but an explicitly advisory
  (`must_pass: false`) case cannot block release indirectly through that
  aggregate. Response caching by (version, case, trial) key makes re-runs
  cheap.
- **Coverage ratchet:** each repo's `.prompteval/inventory.json` lists
  known prompt artifacts (seeded by `prompteval scan`, curated by the
  project session). Inventory entries are `governed` or `ungoverned`.
  The gate warns on ungoverned entries; a project flips
  `"enforce": true` in inventory once its prompts are registered, after
  which ungoverned prompts (and scan-detected likely-prompts missing from
  inventory) fail the gate. New prompts therefore cannot ship ungoverned
  once a repo is enforced — the skill is the remediation path.

### 5. Optimization

- `active` cases are the working set (train/validation as the optimizer
  sees fit); `prompteval score` emits machine-readable per-case results
  with holdout results stripped — that is the interface optimizers
  consume. `holdout` cases live in a separate sealed file
  (`golden/holdout.jsonl`) that iteration workflows never load; they run
  only in `prompteval run --release`. `prompteval check` fails if a
  baseline was accepted without a release run when holdouts exist, or if
  holdout input text appears in the prompt or spec (contamination
  tripwire). **Honest limit, stated on the record:** in a repo-local
  store operated by the same agents who edit prompts, holdout sealing is
  file-separation + tripwires + procedure, not cryptography; an agent
  that chooses to open holdout.jsonl can. The defense is that doing so
  is an unambiguous, greppable protocol violation rather than an easy
  accident.
- Optimized prompts (human, Anthropic improver, GEPA/DSPy-style loop)
  go through the identical gate as hand edits. Never auto-promote.
- The harness exposes `prompteval score` (machine-readable per-case
  scores) precisely so external optimizers can consume it.

### 6. Telemetry and self-monitoring

- Every run/check/gate action appends a typed event to
  `runtime/.telemetry/events.jsonl` (`source: "prompteval"`, correct
  `sourceType`, `eventType` ∈ info|failure|throttled|escalated), per the
  workspace telemetry contract.
- Every LLM attempt appends `eventType: "llm_call"` with provider, model,
  role, status, latency, fallback source, input/output character counts,
  and token accounting. Exact token counts are recorded when a CLI exposes
  them; otherwise the event uses `tokenSource: estimated_chars_div_4`.
  Command reads this telemetry directly so eval cost/latency/fallbacks are
  visible in the principal-facing surface.
- Per S3-P2, staleness/saturation flags that persist ≥3 consecutive
  status runs emit `eventType: "escalated"` so the synthesis loop sees a
  decaying golden set as pressure, not archive.

### 7. Rollout

1. Reference implementation on supervisor-owned prompts (executive lane):
   register a supervisor prompt, generate + audit its golden set, run
   baseline, prove the gate blocks an unevaluated edit.
2. Handoffs to `synaplex` and `command` sessions to run the
   `create-eval-loop` skill on their prompts (synaplex scorer golden set
   seeds from `runtime/intake/scored/` production data on day one).
   atlas/skillfoundry agent charters follow — charters are prompts under
   this contract, graded by judge rubrics on charter-conformance cases.
3. CLAUDE.md amendment (authorized by this ADR — see Consequences).

## Consequences

- `/opt/workspace/CLAUDE.md` Active Decisions gains: **"Every prompt is a
  versioned, eval-gated artifact (ADR-0039)."** New or edited prompts must
  be registered in `.prompteval/` with a golden set and passing baseline
  before deploy; `preflight-deploy.sh` enforces this. Creating a loop is
  the `create-eval-loop` skill.
- Prompt edits get slower by one eval run. This is the point: an
  unevaluated prompt edit is the prompt-layer equivalent of an untested
  code change.
- Eval runs consume subscription budget. Mitigations: response caching,
  small curated active sets, trials only where judges gate, `smoke` tier
  for saturated cases. If budget pressure appears, the harness throttles
  (typed events) rather than silently skipping.
- The judge executes via CLI without temperature control; determinism is
  approximated by trials + majority vote where it matters. Revisit if the
  CLI exposes sampling params or if ADR-0036 is superseded with API keys.
- Golden-set curation becomes a standing responsibility of each project
  session; the reflection loop is the watchdog, not the owner.

## Adversarial review (2026-07-12, Codex, per charter review path)

Initial verdict: "not sound enough to accept — the current contract
overclaims enforcement." All findings addressed before acceptance:

1. *Reference impl lacked a baseline* → baseline run completed and
   committed; the run also caught a wrong golden case (the model
   primary-verifies against the live workspace even in the eval sandbox,
   correctly skipping a fictional proposal as stale) — case corrected,
   stale-state stratum added.
2. *Ungated deploys by default* → gate is now fail-closed for all repos
   (scan-on-no-registry blocks likely prompts).
3. *Criteria weakening undetected* → golden-set hash bound into baselines.
4. *Cache keys too weak for acceptance* → spec/adapter content hashed into
   cache keys; baseline acceptance requires fresh outputs.
5. *Extraction-pointer drift* → spec hash bound into baselines +
   inventory↔spec mapping verification.
6. *Holdouts honor-system* → separate sealed holdout.jsonl, spec-content
   contamination scan, and the honest-limit statement in §5.
7. *Advisory cases gated via paired regression* → regression filter now
   respects must_pass.
8. *ADR overclaimed unimplemented surfaces* → `score` and `align`
   implemented; judge trials wired from spec (was hardcoded 1).
9. *Flywheel could stall silently* → candidate-backlog health flag +
   capture-failure telemetry.
10. *ID/path collisions* → run-id uuid suffix; path-hashed project keys.

Test evidence: 32/32 harness tests pass (including new tests for findings
2–7, 10). The review also indirectly exposed a default-arg binding bug in
the judge caller that had let earlier tests hit the real CLI; fixed.

## Alternatives considered

- **Hosted eval platform (Braintrust/LangSmith/promptfoo cloud):**
  rejected — OpenAI's Evals shutdown (2026-11-30) demonstrates platform
  risk; ADR-0036 forbids the metered API spend they assume; substrate
  doctrine says own the stable layer. promptfoo-the-OSS-tool was
  considered as the runner; rejected for v1 because our executors are
  subscription CLIs, not API providers, and the contract (extraction
  pointers, provenance lifecycle, holdout tripwire, telemetry) is the
  actual value — a thin stdlib harness we own is smaller than the
  adapter layer promptfoo would need.
- **Prompts-as-files migration first, registry second:** rejected —
  forces cross-repo refactors before any eval exists; extraction pointers
  give governance now and make the (still desirable) migration optional
  per project.
- **GitHub Actions as the CI surface:** rejected — no repo uses Actions,
  synaplex has no remote, and runners would need API keys (ADR-0036).
  The preflight deploy gate is where CI already lives here.
- **LLM calls inside the deploy gate:** rejected — gate must be
  deterministic, fast, and runnable offline; the expensive run happens at
  edit time, the gate only verifies its receipt.
