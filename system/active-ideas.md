# Active Ideas

## IDEA-0007 — Intimidation market arbitrage as high-friction market underwriting

- Status: `framed`
- Why it matters: adds a real-world high-friction market sleeve to the
  passive-income portfolio without collapsing the system into manual product
  flipping. The asset should be underwriting, price discovery, fee/logistics
  normalization, and resale-liquidity signal.
- Current state: proposal captured from principal discussion and linked to the
  passive-income portfolio strategy as a candidate sleeve.
- Guardrail: phase 1 is no-inventory paper underwriting only. Buying pallets,
  storing goods, arranging freight, listing products, or handling returns
  requires a separate capital/operations decision after evidence exists.
- Next step: have the PM layer preflight 2-3 auction/recommerce surfaces,
  normalize all-in cost and liquidity risk, track paper-bid outcomes, and
  identify a self-serve monetization route.
- ADRs: none yet.

## IDEA-0006 — Passive income portfolio, not skill-vendor diversification

- Status: `adopted` (ADR-0033 accepted 2026-05-21)
- Why it matters: keeps the workspace from collapsing passive income into
  "more agent-skill marketplaces." Agent tooling is one sleeve; atlas market
  models, data/API products, and research/content licensing are separate
  sleeves with different evidence, risk, and fulfillment profiles.
- Current state: portfolio strategy captured in
  `supervisor/docs/passive-income-portfolio-strategy.md`.
- Next step: route project updates to skillfoundry and atlas so their PM
  surfaces track passive paid events and market-modeling assets, not manual
  sales or single-marketplace exposure.
- ADRs: `0033` (passive income portfolio abstraction).

## IDEA-0004 — Slack signal intake and friction-to-policy automation

- Status: `adopted` (Stage 1 deployed 2026-04-15)
- Why it matters: gives the principal a mobile I/O surface into the
  governance loop without collapsing governance boundaries.
- Stage 1 state: `workspace-slack-notifier.timer` active on 60s
  cadence, posting status cards to `#supervisor-loop` and
  `#workspace-ops` in the Signal Foundry workspace via the
  `workspace-supervisor` bot (token in `config/slack.env`).
- Stage 1 exit gaps: daily digest post, throttling, heartbeat/health
  integration. Track before declaring SLO window complete.
- Stage 2 (inbound `#principal-notes` normalizer): deferred. Requires
  a public Events API endpoint.
- Plan: `/opt/workspace/supervisor/docs/slack-signal-intake-and-policy-automation-plan.md`
- ADRs: `0010` (notes/TRIAGE surface), `0011` (Slack integration
  contract).

## IDEA-0003 — Redesign context-repository around current-state context surfaces

- Status: `pressure_tested`
- Why it matters: fixes a control-plane mismatch between intended and
  actual use of the context repository
- Next step: have the `context-repo` project session produce and begin
  applying a redesign proposal centered on `system/`, `projects/`, and
  `roles/` current state files plus `session_id` provenance in commit
  messages
- Handoff out: `/opt/workspace/runtime/.handoff/context-repo-context-repo-redesign.md`

## IDEA-0002 — Interaction-derived signal triage for compoundable value

- Status: `framed`
- Why it matters: determines whether the system can distinguish noise
  from genuinely compounding signals across ordinary interaction
- Clarification: the important target is not repo shaping directly. It is
  shaping the project-manager layer from principal interaction signals so PMs
  can better shape projects without repeated executive correction.
- Next step: define a signal taxonomy and identify the first source
  surfaces to classify, with explicit categories for:
  - strategic intent
  - architecture pressure
  - policy correction
  - PM shaping signal
  - friction / supervision burden
- Additional rule: interaction signals need confidence grading before
  promotion. A single statement may be:
  - a local correction
  - a sampled preference
  - evidence of a recurring structural principle
  Promotion into policy should depend on seriousness, recurrence, and fit with
  the broader model, not raw recency.
