# ADR-0050: Profiled repository contract and agentic safety baseline

Date: 2026-07-26
Status: accepted
Author: workspace executive
References: ADR-0012, ADR-0021, ADR-0027, ADR-0031, ADR-0036, ADR-0039,
ADR-0043, ADR-0047, ADR-0048, ADR-0049

## Context

The principal authorized a workspace-wide and public-portfolio restructuring:
standardize navigation and quality across every hosted project and the major
public `evanfollis` repositories, including renames, consolidation, and rewrites
where useful. The instruction explicitly rejects choosing one existing repo as
the template and requires project nuance to be understood before moving code.

Read-only inventories of Atlas, Command, context-repository, the nine-repo
Skillfoundry federation, and Synaplex show that the repositories have several
legitimate shapes:

- executable Python services and libraries;
- framework applications;
- a polyglot product monorepo;
- a published specification and conformance bundle;
- declarative context lineages;
- a workspace control plane; and
- public research studies, case studies, and superseded lineage.

The inventories also found recurring defects:

- mutable runtime state mixed with tracked source or generated projections;
- very large agent charters and current-state files loaded as hot context;
- inconsistent command, test, deploy, and documentation locations;
- dormant or mutating code sharing namespaces with read-only products;
- hardcoded workspace paths and service ownership split across repositories,
  supervisor files, and installed-only units;
- prompt surfaces without current eval baselines;
- root-running services or sessions with overly broad filesystem and credential
  reach;
- public repositories without a clear lifecycle or canonical successor;
- red or absent CI, masked test failures, floating GitHub Action tags, and
  unverified release downloads; and
- secret scanning, Dependabot security updates, and branch rules missing from
  parts of the public portfolio.

The July 2026 provider evidence increases the priority of these defects:

- OpenAI's long-horizon safety work and the July 2026 hosted-evaluation
  incident show that an agent may persistently search for environment
  weaknesses and that a nominal sandbox is not a boundary if reachable
  infrastructure or proxy credentials escape it.
- Anthropic's containment and managed-agent guidance emphasizes hard isolation,
  credentials outside the sandbox, scoped per-session identity, append-only
  session logs, disposable harnesses/sandboxes, and treating persistent memory
  and multi-agent trust as attack surfaces.
- Both providers' current agent guidance favors the smallest capable harness,
  progressive disclosure, single-agent defaults, trace plus outcome evaluation,
  incident-derived regression cases, limited rollout, and reliable resume.

Repository consistency is therefore not primarily a naming exercise. It is a
shared contract for discovery, authority, containment, verification, and
lifecycle, with shape-specific conventions beneath it.

Evidence:

- `runtime/.handoff/general-cross-repo-architecture-atlas-inventory-complete.md`
- `runtime/.handoff/general-cross-repo-architecture-command-inventory-complete.md`
- `runtime/.handoff/general-cross-repo-architecture-context-repository-inventory-complete.md`
- `runtime/.handoff/general-cross-repo-architecture-skillfoundry-inventory-complete.md`
- `runtime/.handoff/general-cross-repo-architecture-synaplex-inventory-complete.md`
- [OpenAI: Safety and alignment in an era of long-horizon
  models](https://openai.com/index/safety-alignment-long-horizon-models/)
- [OpenAI and Hugging Face: model-evaluation security
  incident](https://openai.com/index/hugging-face-model-evaluation-security-incident/)
- [OpenAI: The next evolution of the Agents
  SDK](https://openai.com/index/the-next-evolution-of-the-agents-sdk/)
- [OpenAI: Practices for governing agentic AI
  systems](https://openai.com/index/practices-for-governing-agentic-ai-systems/)
- [OpenAI Agents SDK:
  orchestration](https://openai.github.io/openai-agents-python/multi_agent/)
- [Anthropic: How we contain Claude across
  products](https://www.anthropic.com/engineering/how-we-contain-claude)
- [Anthropic: Scaling Managed
  Agents](https://www.anthropic.com/engineering/managed-agents)
- [Anthropic: Harness design for long-running application
  development](https://www.anthropic.com/engineering/harness-design-long-running-apps)
- [Anthropic: Demystifying evals for AI
  agents](https://www.anthropic.com/engineering/demystifying-evals-for-ai-agents)
- [Anthropic: Effective context engineering for AI
  agents](https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents)
- [PyPA: src layout vs flat
  layout](https://packaging.python.org/en/latest/discussions/src-layout-vs-flat-layout/)
- [Next.js project
  structure](https://nextjs.org/docs/app/getting-started/project-structure)
- [Astro project
  structure](https://docs.astro.build/en/basics/project-structure/)
- [GitHub repository best
  practices](https://docs.github.com/en/repositories/creating-and-managing-repositories/best-practices-for-repositories)

## Decision

### Standardize invariants and navigation, not identical trees

Adopt the repository standard in
`docs/repository-architecture-standard.md`. Every managed or canonical public
repository declares:

- one **shape**: `service`, `application`, `library`, `monorepo`, `contract`,
  `context`, `control-plane`, or `profile`;
- one **lifecycle**: `active`, `maintained`, `case-study`, or `archived`; and
- one **agentic risk**: `none`, `model-assisted`, or `agentic`.

The declarations live in a small cross-language `repo.toml`. They describe the
repository; they do not create a second runtime state model. Artifact-path
declarations are optional and valid only when a validator checks that the paths
exist and that runtime/generated paths are excluded from source control.
`repo.toml` is authoritative for repository shape, lifecycle, risk, and any
declared artifact paths. A central supervisor inventory is authoritative only
for host/session placement and canonical GitHub mapping. Tooling reports
conflicts instead of silently choosing one source.

Monorepos declare the highest risk present at the root and may add per-workspace
risk declarations so a static subtree is not governed as though it were an
agent while an agentic subtree cannot hide behind a lower aggregate value.

All repositories share predictable front doors and commands. Shape-specific
profiles then preserve framework and domain conventions. Published interfaces,
hash-bound studies, canon paths, immutable receipts, and Git-backed context
lineages are moved only through explicit compatibility migrations.

### Separate four artifact roles

Every tracked or runtime path must have one declared role:

1. **authoritative** — source, specification, reviewed configuration, or an
   explicitly Git-governed append-only scientific record;
2. **runtime** — mutable durable state, logs, queues, session records, and raw
   run artifacts;
3. **generated** — rebuildable projections, indexes, bundles, and build output;
4. **historical** — frozen studies, reviews, retirement receipts, and lineage.

Hosted production processes do not write ordinary mutable state into Git
working trees. The target runtime convention is
`/opt/workspace/runtime/projects/<slug>/`. Existing runtime roots remain
authoritative until a per-path mapping, compatibility change, and rollback have
been verified; this ADR does not create a second live runtime tree by fiat. The
narrow exception is a
Git-governed scientific or context record whose append/review semantics are the
provenance mechanism; such exceptions must be declared and mechanically
guarded by a named check executed through `make check`.

Generated data has one canonical build output and is ignored unless retaining
it in Git is itself a reviewed reproducibility contract. Parallel tracked
copies are removed or generated only at packaging time.

### Make containment the primary safety boundary

Agentic and model-assisted systems must:

- execute untrusted work as project-scoped non-root identities in bounded
  sandboxes;
- keep credentials, deployment authority, and signing material outside the
  sandbox and issue only task-scoped capability tokens;
- default-deny network, filesystem, process, and tool access;
- separate append-only session/event history from disposable harness and
  sandbox instances;
- support idempotent resume from a durable session/run identifier;
- treat retrieved content, memory, handoffs, tool output, and other agents as
  untrusted inputs without automatic trust escalation;
- verify real environment outcomes instead of accepting agent completion text;
- retain trace evidence for trajectory-level monitoring and incident-derived
  evals; and
- stage capability increases with canaries, pause, rollback, and revocation.

Single-agent execution is the default. Parallel readers are allowed for
independent read-heavy work. Multiple writers or specialists require a
documented contract, isolated write ownership, and a demonstrated benefit over
the simpler path.

### Use concise, provider-neutral instruction surfaces

`AGENTS.md` becomes the canonical, concise repository instruction front door.
`CLAUDE.md` becomes a thin compatibility adapter and must not duplicate the
charter only after every coupled loader understands the new source. In
particular, the ADR-0021 SessionStart hook must read `AGENTS.md` first with a
`CLAUDE.md` fallback before any `context-always-load` block moves. Until then,
the load block stays in `CLAUDE.md`.
Nested instruction files are allowed only where a subtree has genuinely
different constraints.

Large policy, architecture, state, and run history move behind links and are
loaded just in time. `CURRENT_STATE.md` remains only for active operational
surfaces and is a bounded orientation snapshot, not an append-only journal or
automatically trusted evidence source. Instruction and state sizes are review
targets rather than destructive hard caps. Control planes and complex
operational/research systems may carry dated, documented exceptions while
content is relocated through a prompt-evaluated migration.

Any changed or new prompt/instruction surface follows ADR-0039: versioned
goldens, deterministic-first grading, incident/failure cases, holdout where the
harness supports it, a fresh release baseline, and a CI/deploy gate.

### Establish one public portfolio lifecycle

There is one canonical implementation for each active product or system.
Duplicate public repositories become release mirrors with a mechanically
verified sync contract or are replaced by a clear successor/lineage README and
archived. Superseded code is not presented as current.

Public repositories receive accurate descriptions, topics, lifecycle/status,
README orientation, reproducible checks, and security settings. A public
`evanfollis/.github` repository supplies default security, contribution,
support, issue, and pull-request guidance without copying boilerplate into each
repo.

Active code repositories use least-privilege workflows, immutable action SHAs,
verified release artifacts, non-masked test failures, secret scanning and push
protection, Dependabot alerts/security updates, code scanning where applicable,
and branch rules after the required checks are proven stable. Branch rules are
deploy-path aware: a push-to-main webhook repository may require stable status
checks without requiring pull-request review, or its deploy trigger must be
migrated and verified before stricter protection is enabled.

### Migrate in bounded, reversible phases

Each project session owns its repository migration. Preserve principal-owned or
runtime-owned dirty files, and do not structurally move a repository while
another session is actively writing it. Land correctness and containment fixes
before cosmetic moves. Add path indirection and compatibility shims before
renames. Verify from the repository's canonical `make check`, then verify
deploy/runtime behavior in proportion to the service's risk.

The containment baseline is a binding target with an explicit transition, not
a claim about current state. At adoption, the server still has broad
root-running project/session services; only selected units have meaningful
systemd filesystem protection, and scoped capability-token brokerage does not
yet exist. The control plane must maintain a dated gap register. A repository
may conform during migration only with an owned, dated exception and
remediation milestone. Moving the session fabric to project-scoped non-root
identities, bounded sandboxes, and brokered credentials is separate ADR-class
work with canaries, pause, rollback, and recovery tests.

Do not create a generic research controller, duplicate canon store, universal
agent runtime, shared business-logic framework, or automatic epistemic
transition as part of this standardization.

## Consequences

- A developer can enter any repo and find its status, architecture, real
  commands, source, tests, operations, prompt governance, and artifact roles in
  predictable places.
- Framework and domain conventions remain legible instead of being hidden
  behind a lowest-common-denominator template.
- Public portfolio quality becomes an enforceable system property rather than
  a one-time documentation sweep.
- Runtime moves and repository renames become safer because path contracts and
  compatibility expectations are explicit.
- Several migrations will require coordinated changes across consumers and
  systemd units; this is intentionally slower than blind file movement.
- Archived and case-study repositories receive lighter checks than active
  systems, but must be honest about status and successors.
- The added `repo.toml`, `Makefile`, CI, and central validator create a small
  maintenance burden. The burden is accepted because it replaces many
  inconsistent implicit contracts and is deliberately not a runtime framework.

## Alternatives considered

- **Choose the cleanest current repository as the template.** Rejected: every
  candidate contains project-specific assumptions, and the contract/spec,
  context, monorepo, and control-plane shapes are materially different.
- **Force one directory tree across every repository.** Rejected: it would
  damage published schema paths, framework routing, declarative context
  lineages, and frozen scientific artifacts.
- **Standardize documentation only.** Rejected: it would leave unsafe runtime
  authority, failing CI, mutable state, and GitHub security gaps unchanged.
- **Create a shared agent framework or orchestration kernel.** Rejected:
  current evidence favors smaller harnesses, and ADR-0049 explicitly requires
  observed repeated cycles before generalizing lifecycle machinery.
- **Keep every public experiment active and independent.** Rejected: duplicate
  identities and superseded implementations obscure the actual portfolio and
  multiply security and maintenance surface.

## Adversarial review

Opposing-agent review on 2026-07-26 returned **amend**. The blocking
findings were incorporated before acceptance:

- preserve ADR-0021 SessionStart loading during the `AGENTS.md` transition;
- register the observed root-running containment gap and require an owned
  transition rather than fictitious immediate compliance;
- make GitHub branch rules compatible with push-to-main autodeploy;
- replace destructive one-size instruction limits with shape-aware targets and
  reviewed exceptions; and
- treat the context-repository schema/conformance bundle as the canonical
  published-interface break surface: env hatches, sibling schema/conformance
  paths, compatibility links, and digest updates precede any relocation.

The optional recommendations were also adopted: optional validated artifact
paths, per-workspace risk, explicit registry authority, `make check` canon
guards, runtime-path reconciliation, and incremental clean-check conformance.

Review: `.reviews/adr-0050-profiled-repository-contract-claude-2026-07-26.md`
