# Project: skillfoundry-harness

## Current status

- **Active strategic pressure.** Skillfoundry remains the workspace's nearest
  self-serve income surface, but it must not collapse passive income into
  manual LCI sales or one agent-tool marketplace.
- **Preflight lineage reconciled 2026-07-26.** The canonical Preflight
  implementation, release, and deploy source is
  `skillfoundry-products/products/preflight`; the standalone
  `evanfollis/preflight` repo is an obsolete public duplicate / frozen v0.1.0
  snapshot. Treat the standalone as archive-with-pointer material, not as an
  active source or release mirror.
- Under ADR-0033, Launchpad Lint is the first **agent/developer tooling sleeve**
  asset. Its channel matrix is useful, but channel diversification is not the
  same as portfolio diversification.
- Skillfoundry should also look for data/API products that fall out of its own
  discovery machinery: marketplace diffs, launch-readiness metadata, compliance
  feeds, and structured observations.

## What needs to change

- Replace "first external conversation" as the dominant success frame for
  passive-income work. Track first passive paid event, channel-attributed
  activation, repeat use, and low-support fulfillment.
- Keep Launchpad Lint moving across AgenticMarket, RapidAPI, x402, Smithery,
  MCP Registry, and paid skill/plugin surfaces, while explicitly treating that
  as one sleeve.
- Propose at least one non-tooling or data/API passive asset candidate from the
  existing Skillfoundry research/valuation corpus.
- Before implementing Preflight Option A, verify MCP Registry namespace to
  repository binding semantics, then re-home publish identity to the monorepo,
  add a Preflight OIDC publish workflow, and archive the standalone with a
  README pointer. Do not inspect static token values.

## Executive stance

- Push for self-serve, automatically fulfilled experiments. Do not route the
  principal into manual outreach or hand-closing unless they explicitly ask for
  it as a one-off learning sample.

## Active artifact links

- ADR-0033:
  `/opt/workspace/supervisor/decisions/0033-passive-income-portfolio-abstraction.md`
- Strategy doc:
  `/opt/workspace/supervisor/docs/passive-income-portfolio-strategy.md`
- Launchpad Lint channel doc:
  `/opt/workspace/projects/skillfoundry/skillfoundry-products/products/launchpad-lint/docs/MONETIZATION_CHANNELS.md`
- Preflight lineage inventory receipt:
  `/opt/workspace/runtime/.handoff/general-skillfoundry-preflight-lineage-inventory-complete-2026-07-26.md`
