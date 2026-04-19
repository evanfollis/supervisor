# ADR-0026: Agentstack as the third canon instance (publication + evaluation lab)

Date: 2026-04-19
Status: superseded-by-0027
Author: executive, session 847b6afa-1693-46c8-948d-af85a892017a
References: approved plan `/root/.claude/plans/calm-squishing-peacock.md`

> **SUPERSEDED 2026-04-19 by ADR-0027.** The principal articulated, in a
> workspace-root session on 2026-04-19, that `synaplex.ai` is not a parent
> brand over portfolio products but the system itself — a self-evolving
> feedback system whose public surface is synaplex.ai. The "agentstack as
> third-instance sub-brand" framing in this ADR is wrong at the architectural
> level: the lab is not a product alongside atlas and skillfoundry; it is a
> load-bearing layer **of** synaplex. Work landed under this ADR (canon
> adapters on atlas + skillfoundry, first lab Claim pre-registration, Astro
> site scaffold) is preserved as canonical work under ADR-0027. Naming
> retires: `agentstack` / `agentstack.dev` / `agentstack.pages.dev` are not
> used; synaplex.ai is the deploy target. See ADR-0027 §Context for the
> verbatim articulation that forced the supersession.


## Context

Evan has directed the workspace to spread commercial bets across multiple
parallel projects — "revenue inevitability via a portfolio of bets, not
longshots" — with a strong preference for commoditized paths
(`user_revenue_preference_commoditized.md`). He explicitly rejected narrow-
primitive bets ("MCP-as-brand is a RAG-shaped bet"), framing the durable topic
as the architecture of agent systems — harnesses, context, memory,
integrations, orchestration.

He further specified that this new project should rigorously **test** agent
designs and components using the epistemic machinery already under
construction across atlas (crypto) and skillfoundry (commercial discovery),
with three compound outcomes: (a) differentiated content, (b) his own
engineering insight, (c) exercise of the epistemic layer across a third
domain — which is itself the most defensible IP.

Two ground-truth facts established by Phase-1 exploration:

1. **L1 canon exists**, frozen at v0.1.0, at
   `/opt/workspace/projects/context-repository/spec/discovery-framework/`. It
   specifies Claim, Evidence, Decision, Promotion, Realization, Policy,
   EventLogEntry, ArtifactPointer as an *obligations model* (not a state
   machine) with JSON Schemas for all eight and 7 validator-level rules beyond
   schema.
2. **The workspace has pre-committed to "no L2 (runtime) generalization until
   a third domain forces it"** — per `WORKSPACE.md` in the context-
   repository. Atlas is the declared reference instance, skillfoundry the
   declared second instance. Neither has a canon adapter yet.

Competitive landscape: closest-in-lane content peers are solo depth bloggers
(Shrivu Shankar, Philipp Schmid, Raschka, Hugo Bowne). None run a systematic
publication + lab. METR's HCAST+RE-Bench is the only serious third-party eval
treating harness as a variable. "Harness engineering" crystallized as a named
discipline ~Feb 2026; estimated ~12-month window before a labs-backed
competitor claims the surface.

## Decision

**Launch `agentstack` as the third canon instance and the workspace's third
product-tier project** (sibling to atlas and skillfoundry per ADR-0023).
Architecture is **adapter-first, runtime-deferred**:

1. **Every domain emits canon envelopes.** Atlas and skillfoundry each gain a
   thin canon adapter that reads their existing stores and emits envelopes
   conforming to the L1 spec. Agentstack's lab is built canon-native from day
   one.
2. **L2 runtime extraction** (a shared `discovery-runtime` Python package) is
   **deferred** until all three adapters are live and have produced ≥50
   envelopes each. The rule-of-three threshold — workspace policy — fires the
   extraction; it does not fire today.
3. **Editorial launches in parallel** with adapter work on a `agentstack.dev`
   brand (domain registration pending principal confirmation of cost). Daily
   scan + weekly synthesis + directory. No dependency on adapter completion.
4. **First lab eval** (memory systems: Letta / mem0 / MemGPT / Claude memory)
   pre-registers as a canon Claim in Week 5, executes Week 6, publishes with
   adversarial review Week 7–8.
5. **Revenue is commoditized only** — sponsorships, affiliate, paid tier,
   directory listings, benchmark-as-a-service with cryptographic
   `Policy.provenance.sponsor` attestation. No 1:1 services.

## Consequences

**Positive:**
- Canon L1 gets its third instance, vindicating the frozen spec (or exposing
  gaps that bump it to v0.2.0 via adversarial review).
- The workspace gains a public surface demonstrating its epistemic machinery
  to an ~400k-reachable agent-builder audience. The lab output is both product
  and marketing for the underlying IP.
- Atlas's "reference canon instance" obligation (documented but unwritten) gets
  closed as a natural output of this project.
- Skillfoundry's markdown-only epistemic layer graduates to code-emitting-canon
  without disturbing its 367-LOC memory-promotion workflow in `promotion.py`.
- Command gains a unified `/portfolio` view reading all three `.canon/` stores
  — trivial because envelope shape is identical.
- L2 runtime extraction, when it happens (month 5–6), has three real concretes
  to generalize from, not one concrete + two aspirational — so the abstraction
  is grounded.

**Negative / accepted tradeoffs:**
- Three parallel implementations of canon emission live simultaneously for
  several months. This is an explicitly-accepted debt; workspace policy says
  so.
- First published lab piece is 6–8 weeks out. A speed-first competitor could
  ship a less-rigorous eval first. Mitigation: editorial launches Week 3,
  keeping presence in the topic during infrastructure weeks.
- Canon adapter work may surface L1 gaps requiring v0.2.0 spec bump
  (~1-week escalation budget; 2-week fallback to thin compatibility layer).

## Alternatives considered

- **Speed-first fork-Atlas** (Agent 1's draft): copy atlas's models into
  `agentstack/lab-core/`, diverge as needed, ship first eval in 14 days.
  Rejected because it creates a fourth divergent implementation right when
  workspace policy calls for consolidation via rule-of-three. The fast path
  forecloses the real moat (epistemic-system-as-IP).

- **Foundation-first extraction** (Agent 2's draft): extract
  `discovery-runtime` before launching the lab, delay first ship ~6 weeks.
  Rejected because (a) only one concrete exists today (atlas; skillfoundry is
  aspirational markdown) — extracting from one-and-aspirational guarantees
  wrong abstractions; (b) the 12-month competitive window is real. Adapter-
  first captures most of the foundation-first benefits (shared canon contract,
  compounding across domains) without delaying ship.

- **Separate publication and lab brands**. Rejected; reader compounding and
  SEO favor one brand with `/editorial` + `/lab` subpaths.

- **Narrower MCP-only focus** (e.g. `mcpweekly.dev`). Rejected by principal
  explicitly; MCP is a RAG-shaped bet — protocol-level primitives get
  absorbed into the major platforms inside 18 months.

## Implementation plan (summary)

Full plan at `/root/.knowledge/plans/calm-squishing-peacock.md`. Phases:

- **Weeks 1–4 (parallel)**: atlas canon adapter + skillfoundry canon adapter
  + editorial launch (domain, landing, newsletter, daily scan).
- **Weeks 4–6**: lab scaffolding; first eval pre-registered as canon Claim.
- **Weeks 6–8**: first eval executed + adversarially reviewed + published.
- **Weeks 8–16**: cadence + directory + first sponsor path.
- **Weeks 16–26**: paid tier + benchmark-as-a-service + L2 extraction eval.

## Governance

- **Project tier**: Product. Sibling to atlas/skillfoundry under ADR-0023.
- **Shaping surface**: `supervisor/projects/products/agentstack.md`.
- **Reflection loop**: add `agentstack` to `scripts/lib/projects.conf` after
  Week 4 gate (once Current State is stable enough for reflection to produce
  signal).
- **Project-tick timer**: `workspace-project-tick@agentstack.timer` at the
  same cadence as atlas/skillfoundry project ticks. Install after Week 2.
- **Session**: `workspace-session@agentstack.service` systemd template unit
  pinned to `/opt/workspace/projects/agentstack/`. Install after Week 1
  scaffold complete.
- **Reentry**: standard project-session reentry reads `CURRENT_STATE.md`,
  `CLAUDE.md`, any handoffs at `runtime/.handoff/agentstack-*.md`.

## Adversarial review

This ADR commits workspace resources across three repos (atlas, skillfoundry,
context-repository if canon bumps) and adds a new product-tier project. It
warrants Codex adversarial review per workspace convention before any
downstream tick treats it as load-bearing.

Target artifact: `.reviews/adr-0026-2026-04-19T*.md` in `supervisor/.reviews/`,
produced via `supervisor/scripts/lib/adversarial-review.sh`.

Review to be scheduled once the atlas canon adapter has landed a first
working draft (so the review can evaluate ADR + concrete adapter together,
not ADR in isolation).

session_id: 847b6afa-1693-46c8-948d-af85a892017a
