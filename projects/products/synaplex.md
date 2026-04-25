---
name: synaplex shaping surface
description: Executive shaping file for synaplex.ai — the self-evolving knowledge system. Not a product in the portfolio; the system itself. See ADR-0027.
updated: 2026-04-23
tier: system
owner: executive
---

# synaplex — shaping surface

## What this is

synaplex.ai is **the system**, not a product in the portfolio. It is a
self-evolving, self-referential knowledge system whose public face is
`synaplex.ai` and whose operator face is `command.synaplex.ai`. Both faces
look into the same thing. See `supervisor/decisions/0027-synaplex-is-the-system.md`
for the canonical architecture commitment.

Load-bearing layers:

- **Agent context repos** — per-pod / per-agent operational front doors and
  resumability surfaces. Local, mutable, not shared truth.
- **Canon** — formal obligations model at
  `projects/context-repository/spec/discovery-framework/` (frozen at v0.1.0).
- **Knowledge system** — accumulating validated invariants with provenance;
  durable across pod lifecycles and distinct from both canon and local context
  repos. Physical home: open design question (IDEA-0005).
- **Memory / retrieval surfaces** — MCP, file-memory, or managed-memory
  interfaces that let agents consume context and knowledge. Replaceable
  delivery layer, not source of truth.
- **Lab** — methodology engine; pressures canon, validates pod claims,
  reviews external AI systems; produces findings **and** reusable review
  methodologies as first-class assets.
- **Publication + education** — topology not timeline; discovers not
  asserts; each piece builds the latent structure of AI systems.
- **Command** — operator surface; principal's internal view of the same
  system.

Pods (atlas, skillfoundry, future) are exploratory probes with lifecycles.
They have bidirectional obligations to the knowledge system: they uncover
invariants and absorb them. Pod graduation is legitimate.

## Current status

- **Phase**: architecture locked (ADR-0027 proposed 2026-04-19). Legacy
  agentstack work preserved. Deploy to `synaplex.ai` not yet authorized.
- **Tier**: System. Not a portfolio product; the system itself. Atlas,
  skillfoundry, and command are positioned as pods/surfaces of this system,
  not siblings to it.
- **Operating model**: executive shapes; project-session work delegated via
  handoffs under `runtime/.handoff/synaplex-*.md` (naming convention
  changes from `agentstack-*.md`).
- **Session**: `workspace-session@synaplex.service` (formerly
  `@agentstack.service`) — rename pending.
- **Stance**: realist discovery, not opinion publishing. Creative
  pragmatism: ship to uncover invariants; do not anchor on default-blog /
  default-SaaS patterns.

## What "better" looks like

- Public synaplex.ai deployed with a **non-default-blog** site shape —
  minimum-viable topology/concept-map, iteratable.
- First lab evaluation (memory-systems-v1) published as both canon envelope
  and reader-facing writeup; feeds invariants into the knowledge system
  AND produces a reusable review methodology artifact.
- Atlas and skillfoundry CURRENT_STATE docs reframed as pods with explicit
  bidirectional knowledge-system obligations.
- Knowledge system physical home decided (IDEA-0005 → ADR-00XX).
- Review methodologies established as first-class artifacts in canon (new
  type or projection onto Policy — pending context-repository review).
- Subdomain pattern for pods stable: `skillfoundry.synaplex.ai`,
  `command.synaplex.ai`, future `atlas.synaplex.ai`, etc.

## Active pressure points

- **Do not anchor on old/easy patterns.** Default blog post, conventional
  publication site, standard SaaS landing — all rejected by the
  creative-pragmatism constraint. Every page, every publication piece,
  every artifact must be asked: is this shape the right one for a
  self-learning system, or just the one that's easy to build?
- **Do not stay in the clouds.** Ship to uncover invariants; need
  invariants to build the system. Perfection of topology IA is not
  required before V1 deploy.
- **Strange-loop discipline.** Dogfooding is the shape, not a practice.
  Every external review informs how we build our own; every internal tool
  is a candidate for the same review. If a decision breaks that symmetry,
  flag it.
- **Gallery-to-system vigilance.** Every artifact must be an input
  somewhere else. No static content pipelines. No one-off reviews. No
  writeups without canon envelopes.
- **Realist editorial voice.** Less "take," more "what careful looking
  surfaced." If a piece would feel at home on a typical AI newsletter, it
  probably is not synaplex-shaped.
- **Commoditized revenue only.** Per `user_revenue_preference_commoditized.md`.
  No 1:1 services, audits, or consulting, regardless of inbound demand.

## Boundaries

- Executive does not edit synaplex project code directly; delegate to the
  synaplex project PM via handoff.
- Synaplex does not mutate pod-internal stores (atlas's `.atlas/`,
  skillfoundry's `memory/venture/`). Pod adapters produce canon envelopes;
  synaplex reads the knowledge system.
- Synaplex does not treat any runtime memory product as a truth source by
  itself. Retrieval surfaces are delivery mechanisms layered over local
  context repos and/or knowledge-system projections.
- Canon spec changes (v0.1.0 → v0.2.0+) route through context-repository
  adversarial review, not synaplex unilaterally.
- 1:1-delivery revenue surfaces out of scope; any such proposal should
  surface the commoditized alternative instead.

## Truth sources (authoritative for this system)

1. `projects/context-repository/spec/discovery-framework/` — L1 canon.
2. `supervisor/decisions/0027-synaplex-is-the-system.md` — architecture.
3. `projects/synaplex/CURRENT_STATE.md` — front door (rename pending).
4. `projects/synaplex/lab/.canon/` — lab's canonical envelope store.
5. Git history across synaplex, atlas, skillfoundry, context-repository,
   supervisor.

## Interdependencies

- **Atlas**: pod. Contributes hypotheses + evidence as canon envelopes;
  absorbs invariants from the knowledge system back into hypothesis
  generation. Reference canon instance; adapter shipped 2026-04-19.
- **Skillfoundry**: pod. Contributes assumptions/probes/evidence; absorbs
  invariants to refine probe methodology. Adapter shipped 2026-04-19.
- **Context-repository**: owns canon spec. Any gaps discovered during lab
  work escalate via its adversarial-review process.
- **Command**: operator surface for the same system. Gains a portfolio
  view across all pod `.canon/` stores + knowledge system invariants.

## Decision gates (principal)

- **Deploy authorization** — synaplex.ai root to Cloudflare Pages (first
  V1 deploy; reversible).
- **Knowledge system physical home** — IDEA-0005; ADR-class.
- **Legal entity for sponsor revenue** — defer to first sponsor invoice
  (month 5+).
- **Paid tier / education surface monetization** — design-for; defer
  build.
