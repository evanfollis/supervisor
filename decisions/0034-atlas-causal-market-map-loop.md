# ADR-0034: Atlas remains a live causal market-map research loop
Date: 2026-06-09
Status: accepted
Decided by: principal clarification + executive synthesis

## Context

ADR-0033 correctly reframed passive income as a portfolio objective and named
Atlas as the market-modeling sleeve. Subsequent idle-cycle pressure and parked
state summaries overfit that decision into an expand/park/retire framing and
treated runner inactivity as if it were a principal-approved stop.

Evan clarified on 2026-06-09 that he had not decided to stop Atlas. The intended
system is a crypto-market mapping engine that works through falsifiable
hypotheses and conjecture/criticism, uses a causal map to reason about
implications, searches for confounders and alternatives, and records the
reasoning behind actions and non-actions. The desired standard is closer to
Pearl-style causal reasoning than a signal scanner with a promotional graph.

Current live evidence shows an implementation mismatch:

- `atlas-runner.service` is active after the 2026-06-09 reboot.
- The latest runner cycle found signals but generated no hypotheses.
- Atlas has hypothesis, evidence, cycle, and methodology stores.
- `graph/` is empty; live telemetry reports `graph_nodes: 0` and
  `graph_edges: 0`.
- The current graph implementation only grows when a hypothesis promotes to a
  reasoning primitive, so no promoted primitive means no causal-map growth.

Primary handoff: `/opt/workspace/runtime/.handoff/atlas-causal-map-loop-realignment-2026-06-09.md`.

## Decision

Atlas remains the live market-modeling sleeve of the passive-income portfolio.
The default posture is **run and improve**, not stop, park, or remove from
reflection, unless there is a concrete cost, safety, credential, or evidence
quality reason and that reason is routed explicitly.

Atlas must be realigned around a causal research ledger:

- every cycle records either falsifiable action or an explicit no-action
  rationale;
- hypotheses/conjectures include predictions, falsification criteria,
  assumptions, likely confounders, and implications if true;
- observations and closeouts link back to the reasoning that caused action;
- the causal map tracks not only promoted primitives but also contested claims,
  dependencies, contradictions, open confounders, and implications;
- paper-trading or shadow evaluation is preferred when it generates calibration
  data without capital risk.

Prior proposals to suspend Atlas solely because the loop was idle are
superseded by this decision. Idle output is a product/research defect to audit,
not by itself approval to park the system.

## Consequences

- Supervisor and reflection loops must stop asking the principal to choose
  expand/park/retire as the default Atlas question.
- Project-level work should first diagnose why the live runner finds signals
  but produces no hypotheses or graph edges.
- Project-level work should then define the minimum viable causal research row
  and causal-map schema before adding more detectors.
- The existing promotion gate remains valuable, but it cannot be the only path
  by which the causal map learns.
- Atlas may still be paused later, but only via an explicit decision that cites
  measured cost, risk, or evidence-quality failure.

## Alternatives considered

- **Keep ADR-0033 parked-state interpretation**: rejected because the principal
  clarified that no stop decision was made and because it converts idle output
  into governance inertia.
- **Restart and simply add more detectors**: rejected as insufficient. More
  signals do not fix the missing causal-map/criticism/confounder layer.
- **Jump directly to capital allocation**: rejected. Atlas has no promoted
  primitives and no active causal graph, so capital exposure would be premature.
- **Turn Atlas into a paid signal feed immediately**: rejected for now. A feed
  without calibrated predictions, closeout analysis, and causal criticism would
  be semantic theater rather than a robust passive-income sleeve.
