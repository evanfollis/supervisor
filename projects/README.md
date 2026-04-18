# Projects shaping surfaces — tier model

Per ADR-0023, this workspace is a two-tier commercial/epistemic product
system. Per-project shaping files live under two subdirectories
corresponding to their tier.

## products/

External-facing projects whose purpose is to compound commercial or
epistemic value that eventually crosses into revenue.

- `products/atlas.md` — systematic crypto trading/investment system.
  Currently epistemic-first: build a research-backed, tested causal
  model of the market; once a threshold is passed, begin systematic
  investing.
- `products/skillfoundry-harness.md` — venture foundry runtime
  substrate. Skillfoundry as a whole runs Stage-1 commercial discovery
  above this harness (CriticalAssumption → Probe → Evidence → Decision);
  only external evidence classes count.

## system/

Infrastructure projects that the products consume. Principal-facing for
operator use, product-facing for consumption.

- `system/command.md` — executive front door + operator surface. The
  principal's live conversation surface and portfolio view over the
  product projects.
- `system/context-repo.md` — pattern lab for the context-repository
  pattern. Defines the front-door / frontmatter / always-load /
  session-start-hook contract that every other repo in this workspace
  follows.

## Personal projects (off-server as of 2026-04-18)

`mentor` and `recruiter` were demoted to personal side projects and
removed from this server. They remain in GitHub at
`evanfollis/mentor` and `evanfollis/recruiter` with WIP archived on
`archive/mentor-dev-wip-2026-04-18`, `archive/mentor-deploy-wip-2026-04-18`,
and `archive/recruiter-wip-2026-04-18` branches. The principal will
develop them locally on other machines when time permits. They are not
in the persistent reflection / tick loop and should not receive
workspace-level pressure.

See `supervisor/decisions/0023-project-tier-model-and-personal-demotion.md`.
