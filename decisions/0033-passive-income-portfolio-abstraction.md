# ADR-0033: Passive income is a portfolio objective, not a skill-marketplace objective
Date: 2026-05-21
Status: accepted
Decided by: principal

## Context

The workspace goal is to build a system that learns, improves, and can generate
side income without requiring the principal to manually sell. Recent discussion
corrected two overly narrow frames:

- Skillfoundry's Launchpad Lint can use AgenticMarket, Smithery, MCP Registry,
  RapidAPI, x402, and paid skill/plugin marketplaces as distribution or payment
  channels, but those are channel arms for one product family.
- The workspace also contains atlas, a project dedicated to modeling crypto
  market behavior. Treating passive income as "sell more agent skills" ignores
  a separate income sleeve based on market models, signals, research feeds, and
  eventually systematic trading.

The prior reflex was to diversify within the agent-skill/tooling category. The
principal clarified that diversification must happen at a higher abstraction
level than vendor or hosting surface.

## Decision

The workspace will treat passive income as a portfolio objective across multiple
self-serve or automated income mechanisms. Agent tooling marketplaces are one
portfolio sleeve, not the portfolio.

Current portfolio sleeves:

- **Agent/developer tooling**: MCP servers, APIs, paid skills/plugins, hosted
  lint/audit/report tools, and marketplace distribution.
- **Market-modeling assets**: atlas-derived crypto market behavior models,
  signals, research feeds, paper strategies, and eventually automated capital
  allocation only after evidence supports it.
- **Data/API products**: structured feeds created by the system's own work, such
  as marketplace diffs, launch-readiness checks, agent-platform landscape
  signals, compliance metadata, or curated machine-readable observations.
- **Research/content licensing**: synaplex-style explainers, briefs, and
  machine-readable research surfaces that can later be paid, licensed, or
  crawler-monetized.

Every candidate income sleeve must preserve the same operating constraint:
self-serve acquisition, automated or mostly automated fulfillment, and evidence
captured without the principal doing manual sales.

## Consequences

- Skillfoundry should stop treating "first external conversation" as the main
  success metric for passive-income work. The better primary metric is first
  passive paid event by channel, plus repeatable activation evidence.
- Launchpad Lint remains useful, but it is only the first agent-tooling wedge.
  Channel diversification inside Launchpad Lint must not substitute for portfolio
  diversification.
- Atlas is no longer merely an idle project awaiting expand/park/retire. Its
  strategic options should be reframed as whether and how it becomes the
  market-modeling sleeve of the passive-income portfolio.
- Future synthesis and project planning should compare income sleeves by passive
  potential, time-to-learning, capital/risk exposure, automation burden, and
  evidence quality.
- The executive should push PM sessions toward portfolio experiments rather
  than asking the principal to manually sell individual offers.

## Alternatives considered

- **AgenticMarket-first strategy**: fastest to a paid MCP call, but too
  platform-dependent and too narrow.
- **Skill-vendor diversification only**: improves distribution but keeps the
  business confined to one category.
- **Manual LCI/outreach-led services**: potentially useful learning, but violates
  the no-manual-selling constraint unless converted into a self-serve product.
- **Atlas-first trading**: closest to passive income in the pure sense, but not
  yet evidence-ready for capital allocation.

## Follow-up

- Maintain a portfolio strategy doc under `supervisor/docs/`.
- Route project-level updates to skillfoundry and atlas sessions.
- Convert passive-income tracking from offer-level "conversation" metrics to
  portfolio-sleeve evidence metrics.

session_id: codex-2026-05-21-passive-income-portfolio
