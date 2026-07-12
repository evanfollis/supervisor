"""prompteval — workspace prompt-eval harness (ADR-0039).

Every prompt is a versioned, eval-gated artifact. This package owns:
  - the ID contract (one hashing helper for prompt versions, cases, runs)
  - registry: extraction-pointer prompt registration + drift detection
  - golden sets: provenance-labeled cases with a candidate→active→retired
    lifecycle and a sealed holdout tier
  - grading: deterministic checks first, binary LLM-judge checks second
  - runner: subscription-CLI executors (ADR-0036), trials, caching,
    paired baseline comparison
  - the deploy-gate check (pure local, no LLM calls)

Layout per governed repo:
  <repo>/.prompteval/inventory.json
  <repo>/.prompteval/<prompt-id>/spec.json
  <repo>/.prompteval/<prompt-id>/golden/cases.jsonl
  <repo>/.prompteval/<prompt-id>/golden/candidates.jsonl
  <repo>/.prompteval/<prompt-id>/baseline.json
Run artifacts + caches live under /opt/workspace/runtime/prompteval/.
"""

__version__ = "0.1.0"
