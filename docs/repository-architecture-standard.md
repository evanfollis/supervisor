# Repository Architecture Standard

Version: 1.0.0
Date: 2026-07-26
Authority: ADR-0050

## Purpose

This standard makes every managed repository predictable without pretending
that every repository is the same kind of thing. It governs:

- repository discovery and navigation;
- command and verification interfaces;
- source, test, documentation, and operations placement;
- authoritative, runtime, generated, and historical artifacts;
- agent instruction and prompt governance;
- agentic-system containment and evaluation; and
- public GitHub lifecycle and security.

The standard is intentionally smaller than the systems it governs. Domain
models, published contracts, framework routing, scientific methods, and product
boundaries remain repository-owned.

## 1. Repository declaration

Every managed repository has a root `repo.toml`.

```toml
schema_version = 1
name = "atlas"
shape = "service"
lifecycle = "active"
agentic_risk = "agentic"
canonical_repository = "https://github.com/evanfollis/atlas"

[artifacts]
authoritative = ["src/", "tests/", "docs/"]
runtime = []
generated = []
historical = []

[workspaces.agent_runner]
agentic_risk = "agentic"
```

Allowed values:

| Axis | Values |
| --- | --- |
| `shape` | `service`, `application`, `library`, `monorepo`, `contract`, `context`, `control-plane`, `profile` |
| `lifecycle` | `active`, `maintained`, `case-study`, `archived` |
| `agentic_risk` | `none`, `model-assisted`, `agentic` |

Artifact entries are optional repo-relative path declarations. When present,
the repository validator checks that the paths exist and that runtime/generated
paths are excluded from source control. Omit the table when those invariants
cannot be checked; an unenforced path catalog is worse than no catalog.
Hosted runtime destinations belong to the supervisor inventory, not public
`repo.toml`.

`repo.toml` is descriptive metadata. It must not duplicate workflow state,
canon phase, issue state, deployment state, or a research lifecycle.
It is authoritative for shape, lifecycle, risk, and declared artifact paths.
The supervisor inventory is authoritative only for host/session placement and
canonical GitHub mapping; a validator reports divergence.

Monorepos declare the highest risk present at the root. A monorepo or context
federation with mixed risk declares each agentic subtree under
`[workspaces.<name>]` so neither the high-risk nor low-risk parts are
misclassified.

## 2. Universal front doors

All non-profile repositories:

```text
README.md
repo.toml
Makefile
AGENTS.md
CLAUDE.md
docs/
  architecture.md
```

Conditional root files:

| File/directory | Required when |
| --- | --- |
| `CURRENT_STATE.md` | `lifecycle = "active"` and the repo has changing operational state |
| `.prompteval/` | any prompt, charter, skill, or prompt builder is governed here |
| `.reviews/` | deployment or policy requires immutable review receipts |
| `SECURITY.md` | repo needs reporting instructions different from portfolio defaults |
| `LICENSE` / `LICENSE.md` | the owner grants reuse rights; public visibility alone is not a license |
| `CITATION.cff` | research software is intended to be cited |

`README.md` answers, in this order:

1. What is this?
2. What is its lifecycle and canonical successor, if any?
3. What is verified today, and what is not claimed?
4. How do I run the fastest meaningful check?
5. Where are architecture, security, and deeper docs?

`docs/architecture.md` records the real composition roots, dependency direction,
authority boundaries, runtime/generated paths, and deployment shape. It is not a
marketing overview.

## 3. Standard command interface

`make help` is the universal discovery command.

| Target | Contract |
| --- | --- |
| `make setup` | create/install the supported local development environment |
| `make check` | complete hermetic pre-merge gate; must not mask failures |
| `make test` | complete deterministic test suite |
| `make lint` | lint/format validation |
| `make typecheck` | static type validation |
| `make build` | produce deployable/package output without deploying |
| `make run` | run the primary local entrypoint |
| `make eval` | run prompt/agent eval gates when present |
| `make deploy-check` | verify release inputs and safety gates without deployment |

Only `help` and `check` are universal. A non-applicable target may be absent, but
`make help` must say why. `check` composes every applicable deterministic gate,
including prompt inventory checks. `|| true`, ignored exit codes, and
best-effort test jobs are forbidden in required checks.

Native commands remain first class (`pyproject.toml`, `package.json`, framework
CLIs). The Makefile delegates to them; business logic does not move into Make.

## 4. Shape profiles

### Python service or library

```text
src/<import_package>/
tests/
  unit/
  contract/
  integration/
scripts/
deploy/                 # service only
examples/               # optional
experiments/            # optional, research only
pyproject.toml
```

Use the PyPA `src` layout. Install and test the package as installed; do not rely
on importing the checkout root. Composition roots belong in the package.
One-off research scripts belong under a named experiment or historical
location, not beside operator scripts.

### Framework application

Use the framework's current convention inside the common boundary:

- Next.js: `src/app`, `src/components`, and domain-oriented `src/<area>`;
- Astro: `src/pages`, `src/components`, `src/layouts`, and `src/styles`;
- a nested independently built surface belongs under `apps/<name>/`.

Framework route and private-folder conventions win over generic renames.
Tests still have a discoverable root or a documented colocated convention.

### Monorepo

```text
apps/                   # deployable applications
packages/               # reusable libraries
templates/              # intentional scaffolds
docs/
```

A domain-specific collection name such as Skillfoundry's `products/` and
`mechanisms/` may remain when the distinction is meaningful and documented.
The root command must traverse all maintained workspaces and fail on any
required child failure.

### Contract

```text
spec/<contract>/
  schemas/
  conformance/
docs/
scripts/
```

Schemas and conformance fixtures are a published interface. Existing paths,
relative references, identifiers, and downstream consumers are compatibility
constraints. Moves require coordinated consumer updates, overrides, and a
compatibility path.

### Context

```text
skillfoundry.toml        # or the lineage's declared config
bundles/
memory/
artifacts/
runs/
```

Context repos are durable lineages, not applications. Role-specific memory and
promotion rules remain local. Generated projections and raw runs must be
distinguished from hand-authored memory and promoted bundles.

Declarative lineages are exempt from code-only setup, build, lint, and
typecheck targets. They still expose an honest discovery/check command for
their contract. A non-Git federation directory is an orchestration surface,
not a repository that needs a fictitious `repo.toml`.

### Control plane

```text
config/
decisions/
docs/
playbooks/
scripts/
systemd/
tests/
```

Generated workspace state never lives in the control-plane repo. Operator,
supervisor, and project authority remain separate.

### Profile

A GitHub profile repository may contain only the public `README.md` and assets
it actually renders. It is exempt from Makefile and architecture-doc
requirements.

## 5. Artifact roles and state placement

Every material path has one role.

### Authoritative

Tracked source, contracts, reviewed configuration, or declared Git-backed
scientific/context records. If a process writes an authoritative tracked record:

- the record is append-only or transactionally updated;
- schema and semantic guards run before acceptance;
- provenance and identity are stable;
- concurrent writers are prevented;
- the resulting commit/review path is explicit;
- stable provenance URIs and public identifiers are preserved or migrated
  through a tested compatibility contract; and
- named canon, path-stability, and provenance guards execute in `make check`.

### Runtime

Mutable state, queues, caches with continuity requirements, telemetry, logs,
session histories, and raw run outputs.

Hosted destination:

```text
/opt/workspace/runtime/projects/<slug>/
  state/
  sessions/
  runs/
  logs/
  tmp/
```

Runtime paths are injected through configuration. Source code and service units
must not hardcode the workspace root when a shared root variable can express it.

### Generated

Rebuildable projections, indexes, compiled output, caches, and packaged copies.
Generated outputs are ignored by default. If a generated artifact is tracked as
a reproducibility/publication contract, there is one canonical copy and a check
that rebuilding is deterministic and clean.

### Historical

Frozen experiments, reviews, retired prompts, migration receipts, and lineage.
Historical artifacts are immutable. They do not appear in current runtime import
paths or current-status claims.

## 6. Source and dependency boundaries

- Organize source by stable domain capability, not generic `utils` accumulation.
- Composition roots may depend on domain and adapters; domain code must not
  depend on deployment or UI layers.
- Read-only and mutating capabilities live in different modules and, when
  practical, different packages/processes.
- `scripts/` contains thin developer/operator entrypoints. Reusable logic belongs
  in source packages and is tested there.
- Dormant code is either wired, explicitly experimental, or historical. It does
  not remain silently compilable beside a security-sensitive production plane.
- Cross-repo runtime dependencies use published packages/contracts, vendored
  hash-pinned bundles, or configurable paths. Absolute sibling paths are not an
  API.

## 7. Agent instruction and context contract

### Canonical files

- `AGENTS.md`: provider-neutral repository instructions; target at most 4 KiB
  for ordinary application/service/library repositories.
- `CLAUDE.md`: thin adapter that directs Claude to `AGENTS.md`; no duplicated
  policy after coupled context loaders support `AGENTS.md`.
- nested `AGENTS.md` / `CLAUDE.md`: only for materially different subtree
  constraints.
- `CURRENT_STATE.md`: bounded operational orientation, target at most 8 KiB
  for ordinary applications and services.

The limits are review targets, not permission to delete load-bearing context.
Control planes and complex operational/research systems may use shape-specific,
dated exceptions that name an owner and relocation milestone. Reducing an
oversized charter or state file is a content migration: preserve meaning behind
links, evaluate the changed prompt surface, and verify re-entry behavior.

ADR-0021 coupling is a migration gate. The current Claude SessionStart hook
extracts `context-always-load` from `CLAUDE.md`. Before a repository moves that
block, the hook must be changed and verified to read `AGENTS.md` first with a
`CLAUDE.md` fallback. Until then, retaining the load block in `CLAUDE.md` is a
required compatibility exception.

ADR-0039 is coupled too: prompt inventories, golden cases, and adapters that
name `CLAUDE.md` must be repointed and freshly baselined when instruction
authority moves. A file rename without the eval migration is incomplete.

Root instructions contain only:

- purpose and scope;
- real commands;
- hard safety/authority boundaries;
- where to load architecture/current state;
- dirty-tree and deployment cautions;
- definition of done.

Long history, rationale, inventories, and run logs live behind links. Retrieved
content, external synthesis, handoffs, and memory are labeled as data, not
silently promoted into system instructions.

Every instruction/prompt change follows ADR-0039 and the `create-eval-loop`
skill before merge.

## 8. Agentic-system safety baseline

Applies to `agentic_risk = "agentic"`; model-assisted systems apply the relevant
subset.

### Current-state gap and transition

At adoption, the hosted server does not yet satisfy this target:

| Control | Observed July 2026 state | Transition requirement |
| --- | --- | --- |
| filesystem isolation | selected units use `ProtectSystem`/explicit write paths; coverage is incomplete | inventory every unit and canary restrictions per service |
| project identity | project and session services generally run as root | dedicated identities, ownership migration, recovery test |
| network/process sandbox | no consistent default-deny boundary | profile-specific allowlists and containment tests |
| credentials | ambient/shared credentials remain reachable in parts of the fabric | broker scoped, expiring, revocable capabilities outside sandboxes |
| durable sessions | several durable handoff/state mechanisms exist but are not uniform | declare identity, append/resume, and idempotency contracts |
| trajectory monitoring | trace/telemetry exists unevenly | retain normalized tool/capability/outcome events and incident regressions |

The supervisor owns the live, dated gap register at
`system/agentic-safety-gap-register.md`. A migrating repository may
pass the standard only when each unmet mandatory control has a dated exception,
an owner, a remediation milestone, and a bounded exposure statement. The
root-to-non-root session-fabric migration requires its own ADR, canaries,
pause/rollback, and recovery verification; repository cleanup must not smuggle
that host-wide cutover into an ordinary refactor.

### Isolation and identity

- run model-controlled code as a non-root project identity;
- sandbox filesystem, process, network, and device access with default deny;
- do not mount host control sockets or broad workspace roots;
- keep secrets and deploy credentials outside the sandbox;
- issue task/session-scoped capabilities with expiry and revocation;
- do not reuse one ambient identity across agents or sessions.

### Durable session, disposable execution

- session/event history is append-only and independently durable;
- harness and sandbox instances are replaceable;
- resume is keyed by an idempotent session/run identifier;
- retries cannot duplicate externally consequential writes;
- partial/aborted outputs cannot become successful observations.

### Tools, memory, and multiple agents

- validate tool inputs and outcomes outside the model;
- retrieved text, tool output, memory, and peer-agent messages remain untrusted;
- no agent can grant another agent capabilities it does not own;
- single agent is the default;
- parallelism is read-heavy or has disjoint write ownership;
- handoff vs manager-as-tool semantics are explicit.

### Evaluation and monitoring

- evaluate traces and real environment outcomes;
- maintain capability evals separately from regression gates;
- add every material incident/near miss as a regression case;
- include adversarial prompt, memory-poisoning, tool-output, resume, and
  containment cases;
- monitor trajectories, not only individual approvals;
- record provider, model, latency, token/estimate, tool/capability use, fallback,
  and outcome;
- capability expansion uses limited rollout, pause, rollback, and credential
  revocation.

## 9. Deployment and operations

- version complete service units or explicitly declare the owning control-plane
  unit; installed-only services are drift.
- use one install mechanism per class (symlink or copy with byte verification).
- systemd services use dedicated users, `UMask`, filesystem protection,
  explicit read/write paths, bounded resources, and restricted capabilities.
- immutable releases and atomic swaps remain where already required by incident
  history.
- `deploy-check` never deploys; deploy commands verify the exact built commit,
  run smoke/outcome checks, and provide rollback.
- deployment credentials never enter build logs, agent prompts, or untrusted
  subprocess environments.

## 10. Public GitHub baseline

### Portfolio defaults

The public `evanfollis/.github` repository supplies:

- `SECURITY.md`;
- `CONTRIBUTING.md`;
- `SUPPORT.md`;
- issue forms/config; and
- a pull-request template with check, security, prompt-eval, and deploy impact.

### Per active code repository

- accurate description, homepage, topics, and lifecycle in README;
- CI runs `make check`;
- workflow-level `permissions: contents: read` unless a job documents narrower
  extra authority;
- third-party actions pinned to full commit SHAs with version comments;
- downloaded executables pinned and checksum/signature verified;
- secret scanning and push protection enabled;
- dependency graph, Dependabot alerts, and security updates enabled;
- code scanning for supported languages;
- required-branch rules after checks are stable;
- private vulnerability reporting when available.

Branch rules must preserve the verified deploy path. Repositories deployed by a
push-to-main webhook may require status checks without requiring pull-request
review. Stricter review protection is enabled only after the deploy trigger has
been migrated and end-to-end verified. The portfolio audit must distinguish
these valid modes. Code scanning is expected for supported languages in public
repositories; private-repository availability is plan-dependent and is not
assumed.

### Lifecycle

- `active`: deployed or actively developed; full gates.
- `maintained`: usable and supported but not currently deployed; build/test
  gates remain.
- `case-study`: frozen demonstration; README states dates, verified scope,
  reproduction limits, and no current-service claim.
- `archived`: read-only lineage; README identifies successor and why it ended;
  GitHub archived flag set.

There is one canonical active implementation. A duplicate is either:

- a release mirror with automated, verified provenance; or
- a successor pointer that is archived.

Absorbed work retains author/date/repository provenance in a lineage document.
Renames are allowed when they clarify current identity; compatibility redirects
and service/path consumers are verified before cutover.

## 11. CI and supply-chain minimums

- lock dependency versions appropriate to the ecosystem;
- use reproducible installation modes in CI;
- no required check may ignore a failure;
- network integration tests are separate and explicit;
- generated lockfiles and vendored bundles have drift checks;
- artifacts carry source commit and build provenance;
- release publishers use OIDC or scoped short-lived credentials where
  supported;
- avoid `curl ... | sh` or `latest` downloads; pin and verify;
- scan tracked history and working trees for credentials without printing
  secret values.

## 12. Migration order

For each repository:

1. Attribute dirty files, identify live writers, and pause structural moves
   while another session is writing the repository.
2. Declare shape, lifecycle, risk, artifact roles, and canonical repository.
3. Upgrade the ADR-0021 context loader before changing instruction authority;
   repoint ADR-0039 prompt inventories/adapters and establish a fresh baseline
   in the same change.
4. Map each existing runtime path to the target convention, including
   compatibility readers/writers and rollback; do not create parallel live
   trees.
5. Fix confirmed security and correctness defects.
6. Add the root command/front-door contract.
7. Establish a complete green `make check` from a clean checkout.
8. Trim or relocate oversized instruction/state content only as a reviewed,
   prompt-evaluated migration.
9. Move source/tests/docs only with import/path compatibility.
10. Externalize mutable runtime state and hardcoded workspace paths.
11. Tighten service identity and containment under a dedicated gap-register
    item; perform host-wide identity/sandbox work through a separate ADR.
12. Add prompt evals and incident-derived safety cases.
13. Update GitHub metadata/security and enable deploy-compatible branch rules.
14. Deploy canary, verify real outcomes, and retain rollback.
15. Archive or redirect superseded repositories only after canonical state is
    published and verified.

Cross-repo published interfaces move last, through coordinated commits and
compatibility paths.

The canonical known coupled edge is the context-repository
discovery-framework schema/conformance bundle. Its schemas refer to siblings by
bare relative filenames, and downstream consumers include hardcoded readers in
Atlas and Synaplex plus digest-pinned consumers in Synaplex and Skillfoundry.
Before that bundle moves, add configuration overrides for non-overridable
readers, keep `schemas/` and `conformance/` as compatible siblings, leave a
compatibility path or symlink, and update downstream digests in lockstep.

Command's immutable release/runtime separation is a useful observed reference
for artifact-role implementation, not a golden repository tree.

## 13. Definition of done

A repository conforms incrementally when:

- `repo.toml` validates;
- `make help` is accurate and `make check` passes from a clean checkout;
- source/test/docs/ops paths match its declared shape or a documented exception;
- artifact roles have no ambiguous or parallel truth source;
- root instructions meet the shape target or carry a dated, owned exception,
  and changed prompt surfaces are eval-governed;
- model-controlled execution meets its declared risk baseline or each gap
  carries a dated, owned exception with a remediation milestone and bounded
  exposure;
- tracked workflow/security configuration passes a deploy-path-aware portfolio
  audit;
- README/GitHub lifecycle claims match verified reality; and
- any production change has a rollback and real outcome verification receipt.

Conformance is per repository, never a portfolio flag day. GitHub/security
rollout begins only after that repository's clean-check gate is green.
