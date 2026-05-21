# Project: atlas

## Current status

- **Stopped, but strategically important.** The runner was stopped after 16+
  days of zero scientific output; that was correct operator hygiene, not a
  retirement decision.
- Under ADR-0033, atlas is the candidate **market-modeling sleeve** of the
  passive-income portfolio. It should not be evaluated as another tooling
  product or skill marketplace.
- The active strategic question is no longer only expand/park/retire. It is:
  what passive market-modeling asset should atlas attempt first, if any?

## What needs to change

- Reframe the open A/B/C decision around portfolio sleeves:
  - expand research toward a paper strategy or signal feed,
  - explicitly park until a named market-modeling trigger appears,
  - or retire the current pod if the passive-income thesis is weaker than other
    sleeves.
- Keep live-capital trading behind evidence gates. Earlier passive forms can be
  signal feeds, research reports, or paper strategies.
- Maintain correctness pressure on claim hashing and review gaps, but do not let
  those implementation issues obscure the higher-level income-sleeve decision.

## Executive stance

- Maintain atlas as a portfolio-level option, not as idle background noise.
- Do not restart the runner until a passive market-modeling direction is chosen
  or a new signal source/detector makes research productive again.

## Active artifact links

- ADR-0033:
  `/opt/workspace/supervisor/decisions/0033-passive-income-portfolio-abstraction.md`
- Strategy doc:
  `/opt/workspace/supervisor/docs/passive-income-portfolio-strategy.md`
- Principal-decision handoff:
  `/opt/workspace/runtime/.handoff/general-atlas-s3p2-principal-decision-2026-05-10T16-49Z.md`
