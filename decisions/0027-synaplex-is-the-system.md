# ADR-0027: synaplex.ai is the system

Date: 2026-04-19
Status: accepted
Accepted: 2026-04-20
Review: .reviews/adr-0027-2026-04-19T15-42Z.md
Supersedes: ADR-0026
Author: executive, workspace-root session 2026-04-19T14:xxZ
References: ADR-0026 (superseded), ADR-0023 (project tier model)

## Context

Between 2026-04-19T14:10Z and 2026-04-19T14:50Z (approx.), the principal
articulated — across five conversation turns — the latent structure he had
been "searching and circling" for. The articulation reshapes what was
previously scoped as `agentstack` (ADR-0026) into something materially
different.

The prior framing treated the new project as a third sub-brand (publication +
evaluation lab) sitting alongside atlas and skillfoundry under a portfolio
umbrella. The principal's articulation rejected that framing in two stages:
first rejecting `agentstack.dev` as a standalone brand in favor of the
existing `synaplex.ai`; then rejecting the implicit premise that synaplex.ai
was merely a parent brand over portfolio products. His articulation:

> "synaplex.ai is the latent structure I am searching and circling... atlas
> and skillfoundry are just surfaces of that larger latent structure. The lab
> becomes the machine that powers/informs all of the variations of the
> projects that exist and will exist... Synaplex.ai can be that window into
> the larger system that we are uncovering."

And further:

> "Skillfoundry and Atlas are exploratory pods... The invariants we uncover
> will remain and get adopted into synaplex.ai's knowledge system and will
> inform new projects and improve existing projects."

And further:

> "We aren't building a gallery. We are building a system — a self-learning,
> self-evolving feedback system... there are many 'strange loop' layers where
> we are using AI systems to uncover and build AI systems and this is
> happening at the component level all the way up to the full system.
> Synaplex.ai IS that system."

And further:

> "Publication pieces aren't a timeline of events; new pieces further build
> and refine the latent thing that is AI systems. We are seeking to uncover
> that shape and share it with the community. AI systems education is also a
> natural surface."

And finally:

> "We want to command the space, not be drug by it... We have to maintain
> this creative pragmatism at all costs."

This ADR captures that articulation as a durable commitment, supersedes
ADR-0026, and records the architectural consequences.

## Decision

**synaplex.ai is the system.** Not a parent brand, not a publication, not a
portfolio surface. The system itself — with a public face at `synaplex.ai`
and an operator face at `command.synaplex.ai`.

Load-bearing layers:

1. **Canon** — the formal obligations model at
   `projects/context-repository/spec/discovery-framework/` (frozen at
   v0.1.0). Every claim, evidence, decision, and policy across the system
   validates against it. The canon is itself a claim about how claims are
   made, so it is subject to its own validator — the first strange loop.

2. **Knowledge system** — the accumulating body of validated invariants,
   with provenance back to the pod evidence or lab reviews that produced
   them, and forward pointers to the pods and reviews that currently consume
   them. Durable across pod lifecycles. Physical home is an open design
   question (see §Open design questions below).

3. **Lab** — methodology engine. Pressures canon. Validates pod-generated
   claims. Reviews external AI systems, producing two durable outputs:
   (a) object-level findings about those systems and (b) reusable **review
   methodologies** that re-enter the knowledge system as first-class assets
   and feed back into how we design our own components. Dogfooding is
   structural, not incidental.

4. **Publication + education surfaces** — the public-facing projection of
   the knowledge system. The publication is **topology, not timeline**: each
   new piece builds and refines the latent structure of AI systems; old
   pieces do not age out but become foundations for newer ones. Information
   architecture reflects conceptual topology, not publish-date. Education is
   a **natural surface** of the knowledge system when turned toward a
   learner — not a separate product to build, but an emergent projection to
   design-for.

5. **Command** — operator surface. The principal's internal view into the
   same system the public sees externally through synaplex.ai. Internal and
   external views are faces of one system, not separate products.

**Pods** (atlas, skillfoundry, future) are exploratory probes. Their
relationship to the knowledge system is **bidirectional** — they uncover
invariants; they absorb invariants already in the system. They have
lifecycles: emerge, explore, contribute, evolve, graduate, or deprecate.
Pod graduation is legitimate, not failure. What persists across pod
lifecycles is the knowledge system; what transits through pods are
invariants and review methodologies.

**Exploration is broader than pods.** External exploration includes the
lab's review of external AI systems, daily news ingestion, directory
construction, community engagement, and education production. All feed the
knowledge system.

**Strange-loop structure is architectural, not decorative.** We use AI
systems to review AI systems to build AI systems. Canon validates canon.
The tools are the objects. This recursion is the generative engine, not a
philosophical flourish.

**Stance: realist.** AI systems have real structure that exists before
anyone writes it down. The publication **discovers**; it does not assert.
Editorial voice follows: less "my take on X," more "this is what careful
looking surfaced."

**Operating discipline: creative pragmatism.** Two failure modes to avoid:
(a) anchoring on old/easy patterns — default blog-post site shape,
conventional AI publication format, standard SaaS pages; (b) staying in the
clouds — over-designing the topology IA, deferring ship indefinitely, never
producing invariants to build around. Ship to uncover invariants; need
invariants to build the system. Hold both at every turn.

## Consequences

### Naming and retirement

- `agentstack` retires as a brand name. Every external and internal
  reference migrates to `synaplex.ai` / `synaplex`.
- `projects/agentstack/` renames to `projects/synaplex/`. The project is
  the codebase for synaplex.ai itself (publication + lab machinery +
  knowledge system runtime), not a separate product.
- `supervisor/projects/products/agentstack.md` is superseded by
  `supervisor/projects/products/synaplex.md` (which replaces the shaping
  surface, not adds a new one).
- `agentstack.dev` domain is not registered. `agentstack.pages.dev` is not
  provisioned.

### Deploy target

- Deploy target is `synaplex.ai` root (apex or `www` subdomain of the
  existing Cloudflare zone). The existing subdomain pattern continues for
  pod-surface deployments:
  `skillfoundry.synaplex.ai`, `command.synaplex.ai`,
  `api.synaplex.ai`, future pods at `<pod>.synaplex.ai`.
- Public DNS for synaplex.ai is already in Cloudflare (migration from
  Namecheap underway per active-issues.md); no new registrar transaction.

### Site shape

- Information architecture reshapes away from the Astro scaffold's current
  blog/lab/directory split (chronological feeds inside each category)
  toward concept-map / topology. V1 ship does not require the finished IA;
  it **does** require explicitly not anchoring on default-blog conventions.
  Creative pragmatism: ship a minimum-viable concept-map shape, iterate.
- Copy reshapes from "agentstack — publication + evaluation lab" framing to
  "synaplex.ai — discovering the structure of AI systems" (or similar; copy
  is a subsequent pass, not part of this ADR).

### Pod reshaping

- `projects/atlas/CURRENT_STATE.md` and
  `projects/skillfoundry/*/CURRENT_STATE.md` reshape themselves to frame
  the project as a **pod** with bidirectional obligations to the knowledge
  system (both uncovering and absorbing invariants). Pod lifecycles
  (including graduation) are now legitimate and documented.
- Canon adapter work landed 2026-04-19 is preserved. No code regresses.

### Work preserved from the agentstack plan

- Canon adapters shipped on atlas + skillfoundry remain canonical work.
- First lab Claim pre-registration (`memory-systems-v1`) remains canonical
  work, now understood as the first lab evaluation under synaplex, not
  "agentstack's first eval."
- Astro scaffold remains the starting point for synaplex.ai's site, to be
  rebranded and IA-reshaped.

## Open design questions (not resolved by this ADR)

1. **Knowledge system physical home.** Candidates: a new artifact type
   inside `projects/context-repository/`; a top-level directory inside
   `projects/synaplex/`; a hybrid with context-repository hosting formal
   invariants and synaplex hosting editorially-projected ones. Requires a
   small design pass + IDEA ledger entry before commitment. Tracked as
   IDEA-0004 (to be created).

2. **Site IA beyond "not a blog."** Minimum-viable topology shape for V1
   deploy — topic map? conceptual taxonomy? "start here" entry node +
   linked explorations? Pragmatism demands a shippable V1 that is not
   default-blog; perfection not required before first deploy.

3. **First publication piece editorial voice.** Discovers-not-asserts is
   settled; concrete voice + first topic is not. Candidate first piece:
   the memory-systems-v1 evaluation, published as both canon envelope and
   reader-facing writeup.

4. **Education surface physical shape.** Design-for now, build-later.

5. **Lab review methodologies as first-class artifacts.** Canon currently
   types Claim / Evidence / Decision / Policy / Promotion / Realization /
   EventLogEntry / ArtifactPointer. Review methodology may be a new type,
   or may project onto Policy. Requires context-repository adversarial
   review before spec bump.

## Alternatives considered

- **Keep ADR-0026 as-is** (agentstack as a third sub-brand).
  Rejected by principal articulation; synaplex.ai is the system, not a
  parent over sub-brands.
- **synaplex.ai as umbrella brand, agentstack.synaplex.ai as lab subdomain**
  (a subdomain variant proposed mid-conversation).
  Rejected after further articulation: the lab is not a product under
  synaplex; it is a load-bearing layer **of** synaplex. Subdomain would
  fragment what is architecturally unified.
- **Staged migration: launch agentstack first, rebrand later.**
  Rejected: migration cost plus the risk of anchoring brand equity in the
  wrong identity outweighs the (small) convenience of not pausing to
  rename.

## Adversarial review

This ADR is consequential — it reshapes the workspace's top-level brand
architecture and redefines atlas/skillfoundry's self-description. It
warrants Codex adversarial review via
`supervisor/scripts/lib/adversarial-review.sh` before status transitions
from `proposed` to `accepted`.

Target artifact: `.reviews/adr-0027-<iso>.md`.

Review scope: pressure-test the synaplex-is-the-system framing against
(a) brand-architecture best practices (subdomain vs parent-brand tradeoffs
at this stage of audience building), (b) the strange-loop claim's
architectural testability, (c) the creative-pragmatism discipline's
enforcement mechanism, (d) whether superseding ADR-0026 before its own
review completes creates governance drift.

## Provenance

Articulated across five conversation turns with the principal on
2026-04-19, workspace-root session at `/opt/workspace`. Load-bearing
principal statements preserved verbatim in §Context.

session_id: [workspace-root executive session 2026-04-19]
