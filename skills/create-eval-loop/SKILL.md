---
name: create-eval-loop
description: Create a versioned, CI-gated evaluation loop for a prompt — golden set, graders, baseline — using the prompteval harness (ADR-0039). Use whenever a prompt exists or is being created without one.
applies_to: any-agent
---

# Create an Eval Loop for a Prompt

Every prompt that runs in this system must be a versioned, eval-gated
artifact (ADR-0039). If you are about to edit, create, or ship a prompt
that has no `.prompteval/<id>/` entry in its repo, **stop and run this
skill first**. The deploy gate (`preflight-deploy.sh`) blocks any edit to
a governed prompt that lacks a fresh passing eval, and enforced repos
block ungoverned prompts entirely.

Harness: `/opt/workspace/supervisor/scripts/prompteval` (docs in
`scripts/lib/prompteval/*.py` docstrings). All LLM work here runs through
subscription CLIs (`claude -p` / `codex exec`) per ADR-0036 — never
metered API keys.

## When to use

- A prompt exists in this repo with no eval loop (check: does
  `.prompteval/<some-id>/spec.json` point at it?)
- You are writing a new prompt (create the loop in the same change)
- `prompteval check` failed with "ungoverned prompt" or a handoff asked
  you to bring a prompt under governance
- A golden set is flagged stale/saturated/synthetic-majority and needs
  refresh (jump to step 6)

## Step 1 — Identify and register the prompt

Find the prompt's single source of truth. If unsure what counts as a
prompt in this repo, run `prompteval scan .` — anything that shapes model
behavior (system prompts, prompt builders, agent charters, SKILL files)
counts.

Pick the tightest extraction pointer (prefer the top of this list):

| Prompt form | source type | notes |
|---|---|---|
| Dedicated file (`*-prompt.md`) | `whole_file` | |
| Section of a file | `region` | add `<!-- pe:begin -->`/`<!-- pe:end -->` markers |
| Python string constant | `py_var` | plain constants only; f-strings need `region` markers or a refactor to a constant + `.format` |
| TS template literal / other | `regex` | one capture group; last resort — prefer refactoring the literal to a dedicated file |

Choose the executor — **prefer the real runtime path**:

- `command` + a small adapter script in the repo that invokes the actual
  runtime function (reads `{prompt_text, model, params, input}` JSON on
  stdin, prints raw model output). This evals what production actually
  runs. Note ADR-0036: if the runtime path needs an API key the repo
  doesn't have, fall back to `claude_cli`.
- `claude_cli` — harness sends the extracted prompt as system + a rendered
  `user_template`. Good approximation for text-transform prompts.
- `codex_cli` — cross-family execution when the prompt targets Codex.

Register (id: kebab-case, stable, descriptive — it is permanent):

```bash
prompteval register . --id <prompt-id> --file <path> --type <type> [--var X | --begin A --end B | --pattern P] \
  --model <runtime-model> --judge-model <different-tier> \
  --executor <type> --user-template '<template with {input_fields}>' \
  --description '<what this prompt does>'
```

Judge model must be a **different tier/family than the target model**
(target sonnet → judge opus; target-is-claude + self-preference-sensitive
→ consider a codex judge via a `command` adapter). Set `--trials 3` if
judge checks will gate this prompt (majority vote absorbs judge noise).

## Step 2 — Golden set: seed from reality first

**Order of preference for inputs (never skip a tier that exists):**

1. **Real logged inputs** — telemetry, JSONL logs, transcripts of actual
   calls to this prompt. Capture directly:
   ```bash
   prompteval capture . --id <id> --from-jsonl '<glob>' --fields f1,f2 --output-field <observed> --limit 25
   ```
   Then promote curated ones (step 4). These are `production` provenance
   from day one.
2. **Real failures** — anything this prompt has gotten wrong (friction
   logs, reflections, bug reports). Each becomes a must-pass regression
   case. The best golden sets are built from failures, not successes.
3. **LLM-generated synthetic** — only to fill coverage gaps, via the
   dimension-tuple method below. Labeled `synthetic` forever, and expected
   to phase out as production cases accumulate.

**Dimension-tuple synthetic generation (never "give me N test inputs"):**

1. Enumerate the axes of variation for this prompt's input space (e.g.
   for a relevance scorer: source-type × topicality × hype-level ×
   length × noise-type). Write them down in the spec dir as
   `golden/dimensions.md`.
2. Hand-pick 12–30 tuples covering: the common strata (mirroring real
   traffic), every edge stratum (empty/very long/wrong-language/
   adversarial/ambiguous-even-for-humans), and both positive AND negative
   expected outcomes (a set where everything should pass teaches nothing).
3. One `claude -p` call per tuple batch to render tuples into realistic
   inputs. Add perturbations (typos, irrelevant detail) to a few.
4. **Audit every synthetic case yourself** before activating: is the input
   realistic? Is the expected outcome actually correct? Would a domain
   expert agree? Delete anything you had to squint at. An unaudited
   synthetic case is worse than no case — it can gate real improvements
   out.

Start with **12–50 active cases**. Small and sharp beats large and mushy;
grow with production captures.

## Step 3 — Checks: deterministic first, judge second

For each case, write `checks` in this order:

1. **Deterministic** (free, exact): `json_valid`, `json_schema`,
   `numeric_band`, `contains`/`not_contains`, `regex`, `length_band`.
   If the prompt output has ANY structure, assert it here. Most
   prompts can be 70%+ graded deterministically.
2. **Judge** — only for genuinely subjective dimensions. One check per
   **named failure mode** with a binary rubric, never one mega-rubric,
   never a 1–10 score:
   ```json
   {"kind": "judge", "failure_mode": "score-inflation",
    "rubric": "FAIL if the output rates marketing/hype content as if it were primary technical material. PASS if hype is scored low with a rationale naming why."}
   ```
   A good rubric names concrete evidence the judge should look for. If
   you can't write a binary rubric for it, you don't know what failure
   you're checking — go back to error analysis.

   Judge accountability: the first time a human (or you, on review)
   disputes a judge verdict, record the disputed output + the correct
   verdict in `.prompteval/<id>/judge/alignment.jsonl`
   (`{"failure_mode", "rubric", "case_input", "output", "human_verdict"}`).
   `prompteval align . --id <id>` then reports the judge's TPR/TNR against
   those labels and fails below 0.8 — a judge that can't clear that bar
   gets its rubric revised before it gates anything. Set
   `judge.trials: 3` in the spec for majority-vote self-consistency on
   judges that gate.

Criteria describe **what makes an output acceptable, not what the model
said last time**. Never paste an observed output as an `exact` check for
an open-ended prompt — that freezes today's phrasing, not quality.

Mark exploratory cases `"must_pass": false` (recorded, doesn't gate).

## Step 4 — Cases file, holdout, baseline

Write cases via a short Python snippet (IDs are minted from inputs —
never hand-write ids):

```python
import sys; sys.path.insert(0, '/opt/workspace/supervisor/scripts/lib')
from prompteval.goldens import new_case
from prompteval.core import append_jsonl
case = new_case(input_obj, checks, provenance="synthetic",  # or production/human
                source="dimensions.md tuple 7", notes="edge: empty summary")
append_jsonl(".prompteval/<id>/golden/cases.jsonl", case)
```

Promotion of captured candidates instead: write `plan.json` mapping
candidate id → checks, then `prompteval promote . --id <id> --plan plan.json`.

**Seal a holdout**: once you have ≥12 active cases, move 2–4
representative ones to holdout via
`python3 -c "...goldens.set_status(spec_dir, case_id, 'holdout')"` —
they live in a separate `golden/holdout.jsonl` file precisely so
iteration and optimizer workflows reading the working set never load
them. **Do not open holdout.jsonl during iteration.** They run only in
`run --release --yes` when accepting a baseline. Don't quote holdout
contents in prompts, specs, or notes (the gate has a contamination
tripwire scanning both).

Then baseline — acceptance requires **fresh outputs** (`--no-cache`);
cached outputs are for cheap iteration, not for accepting a baseline:

```bash
prompteval run . --id <id> --release --yes --no-cache --update-baseline
prompteval check .        # must PASS now
```

Read the failures before touching anything. A failing case at baseline
time means either (a) the prompt has a real defect — fix the prompt, not
the case — or (b) the case/criteria are wrong — fix them and note why.
Radical truth applies: do not massage criteria until green without
understanding which of the two you are doing.

## Step 5 — Wire the flywheel and the ratchet

1. **Capture**: ensure the runtime path logs its real inputs (+outputs)
   somewhere JSONL-reachable, and add a `prompteval capture` invocation to
   the project's existing scheduled loop (tick, cron, or deploy script) so
   candidates accumulate without anyone remembering to do it.
2. **Inventory**: update `.prompteval/inventory.json` — mark this prompt's
   file `governed`, list any remaining prompt files `ungoverned`. When the
   last one flips governed, set `"enforce": true`. From then on the deploy
   gate fails on any new ungoverned prompt — the ratchet only tightens.
3. Commit `.prompteval/` with the change that introduced/edited the
   prompt. The eval loop and the prompt travel in the same diff.

## Step 6 — Keep it alive (refresh triggers)

`prompteval status . --source-type cron` runs from scheduled loops;
reflection reads its output. Act on flags:

- **stale** (cases >90d unvalidated): re-read each stale case against
  current reality; bump `last_validated` if still right, retire if the
  system has evolved past it. The golden set tracks *current*
  expectations, not founding-era ones.
- **saturated** (all-pass streak ≥5): the set has stopped teaching.
  Move the easiest cases to `"status": "smoke"`, promote fresh captures,
  add cases from recent failures.
- **synthetic-majority** (production ratio <0.5 on a mature loop):
  capture + promote more production cases; retire synthetic cases whose
  stratum is now covered by real ones. Target: production-majority.
- 3 consecutive flagged status runs auto-emit an `escalated` telemetry
  event — if you see one, this maintenance is overdue, do it now.

## Optimizing a prompt against its loop

Iterate on `active` cases freely (that's what they're for). You may split
them train/validation if using an automated optimizer (GEPA/DSPy-style):
`prompteval score . --id <id>` emits machine-readable per-case results
from the latest run, with holdout results stripped. **Never look at
holdout.jsonl while iterating.** Accept the final candidate only via
`run --release --yes --no-cache --update-baseline`, and read the holdout
results in the report — a candidate that wins on active and loses on
holdout is overfit; revert it. Optimizer output goes through the same
gate as hand edits. Never auto-promote.

## Definition of done

- [ ] `spec.json` registered; `prompteval show` prints the exact live prompt
- [ ] 12–50 audited active cases; failures-and-edges represented; both
      expected-pass and expected-fail outcomes present
- [ ] Checks are deterministic-first; every judge check names one failure
      mode with a binary rubric
- [ ] 2–4 holdout cases sealed (or a dated note in spec `description` why not yet)
- [ ] `prompteval run --release --yes --no-cache --update-baseline` GATE: PASS
- [ ] `prompteval check .` passes; inventory updated; enforce ratchet
      advanced if this was the last ungoverned prompt
- [ ] Capture wired into a scheduled loop
- [ ] `.prompteval/` committed alongside the prompt change
