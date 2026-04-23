---
name: Positioning test for AI-era products and pods
description: Two heuristics for evaluating whether a product/pod position strengthens or erodes as model capability compounds. Apply to any synaplex pod, skillfoundry probe, or atlas component at the decision point where architecture, wedge, or pricing is being chosen.
updated: 2026-04-21
owner: executive
source: ChatGPT conversation 69e6be44 (2026-04 thread on AI market positioning), captured 2026-04-21
---

# Positioning test

Two compressing questions. Use them at the design-decision moment, not as post-hoc rationalization.

## Heuristic 1 — The 10× test

> When models get 10× better and 10× cheaper, what happens to us?

**Strong position** (better models make you more central):
- throughput explodes
- margins improve
- product becomes more valuable
- more tasks flow through our layer
- data / eval / memory advantage deepens
- switching cost grows
- the frontier provider *cannot* absorb us without also absorbing a workflow, a system of record, or a trust boundary they don't own

**Weak position** (better models erode you):
- our differentiation disappears
- the model provider can absorb us
- customers can rebuild us with raw access
- the value was in prompt quality, framing, or a thin wrapper

The test is not "are we using AI" or "is our AI good." It is whether capability compounding is our friend or our executioner.

## Heuristic 2 — Downstream-of-capability, upstream-of-value

> The durable position is downstream of capability improvements but upstream of customer value capture.

Let others race on raw capability. Own:
- the trusted workflow
- the compounding data and eval loop
- the economic chokepoint (system of record, system of action, transaction surface)
- architectural optionality while the stack is still moving

"Freeze the contracts, not the guts." Hard commitments at interfaces, telemetry, data contracts. Soft commitments on models, UX, internal implementation.

## How to apply

At each of these decision points, run both tests:

| Decision | Apply to |
|---|---|
| New pod or probe proposed | Evaluate the wedge *and* the upward architecture — does the wedge point at a durable control point, or does it end at a disposable feature? |
| Pricing model chosen | Does the meter track controllable units today while pointing toward outcome economics? |
| Model / provider lock-in considered | Can the contracts stay rigid while the guts swap? |
| Adjacent-task expansion decided | Are we moving toward the action layer and system-of-record status, or just adding surface area? |
| New feature prioritized | Does shipping this deepen our embeddedness, or does it sit flat inside someone else's durable layer? |

## Failure mode to avoid

Mistaking adoption for defensibility. Being part of a new wave is not enough. Many firms in every platform shift helped popularize new behavior but did not own the economics. Visibility ≠ control point.

## Related

- `supervisor/ESSENCE.md` — the worldview positioning serves
- `supervisor/projects/products/synaplex.md` — the synaplex shaping surface where pod positioning decisions land
- `supervisor/ideas/IDEA-0005-knowledge-system-physical-home.json` — a current decision surface that should pass both heuristics before commitment
