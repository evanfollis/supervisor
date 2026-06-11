# ADR-0036: Token budget — subscription plans only, no metered API spend

Date: 2026-06-11
Status: accepted (principal directive, captured verbatim per ADR-0025)

## Context

Principal statement (2026-06-11, attended session): "I currently have the
$100/month Anthropic and OpenAI plans ($200/month total). I don't want to
burn more tokens than what is allowed there. If we hit limits, then we
should pause or rely on the unblocked provider."

Synthesis cycles C72–C92 carried "provision ANTHROPIC_API_KEY for synaplex"
as a standing recommendation (21 cycles). That key would enable Sonnet
scoring/synthesis at ~$3/day (~$90/month) of metered API billing — spend
outside the subscription plans.

## Decision

- AI spend is capped at the two existing subscriptions: Anthropic $100/mo
  and OpenAI $100/mo. No metered API keys are provisioned without a new,
  explicit principal authorization.
- The synaplex Sonnet scorer/synthesizer remains on the heuristic path.
  This is a deliberate cost decision, not a credential blocker. Reflection
  and synthesis jobs must stop carrying it forward as a blocker.
- If a provider's subscription limit is hit, agents pause that provider's
  work or route to the unblocked provider (Claude ↔ Codex), not to metered
  API fallbacks.
- Workspace loops and attended sessions should economize accordingly:
  prefer single-session work over multi-agent fan-outs unless explicitly
  requested; heavier models only where the charter already calls for them.

## Consequences

- C92 standing recommendation #6 closes as "deferred by decision."
- Synaplex Layer 2 design proceeds, but its build plan must assume
  subscription-budget execution (CLI sessions) rather than API billing,
  or wait for explicit authorization.

## Alternatives considered

- Provision the key with a hard monthly cap: rejected — caps on metered
  billing still create spend outside the stated budget envelope.
