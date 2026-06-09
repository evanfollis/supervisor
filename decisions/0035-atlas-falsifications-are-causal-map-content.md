# ADR-0035: Atlas falsifications are causal-map content
Date: 2026-06-09
Status: accepted
Decided by: principal clarification + executive synthesis

## Context

ADR-0034 restored Atlas as a live causal market-map research loop. The Atlas
project audit (`/opt/workspace/projects/atlas/CAUSAL_LOOP_AUDIT.md`, commit
`b0df455`) found a cold-start deadlock:

- signal intake finds 22 candidates per cycle;
- all 22 deduplicate to already-tested claims;
- 69 of 76 stored hypotheses are `FALSIFIED`;
- 0 hypotheses have ever promoted to reasoning primitives;
- `graph/causal_graph.json` has never been created;
- `from_graph_gaps()` returns `[]` when the graph is empty.

The current graph only learns when a claim is positively promoted. This loses
the strongest evidence Atlas has produced so far: tested absence of an effect.
It also contradicts the principal's 2026-06-09 clarification that the map should
capture implications, contradictions, confounders, and "what cannot hold if
this does."

## Decision

Atlas should represent falsified claims as first-class causal-map content, but
not as high-trust positive reasoning primitives.

The graph/model layer must distinguish at least:

- **promoted/supportive claims**: high-trust primitives that survived the
  promotion gate;
- **refuted/null-effect claims**: tested claims with enough contradictory
  evidence to be killed;
- **open/contested claims**: conjectures or implications under evaluation, if
  the implementation adds them;
- **relationships**: supports, contradicts, excludes, weakens, refines, tests,
  and potential-confounder links where evidence justifies them.

Falsifications should be usable for graph-gap generation, future conjecture
selection, no-action explanations, and "what cannot co-hold" reasoning. They
must not be labeled as profitable signals, live-trading edges, or promoted
primitives.

## Consequences

- Atlas can learn from negative evidence instead of treating 69 falsifications
  as terminal waste.
- The empty-graph cold-start deadlock has a principled escape path: backfill
  falsified claims into the map, then generate future work from refuted regions,
  contradictions, and untested confounders.
- `atlas graph show` and related telemetry must report graph content by status
  or trust class, not only node/edge count.
- The promotion gate remains intact and conservative. This ADR changes map
  semantics, not trading readiness.
- Existing graph consumers must tolerate mixed-status nodes and edges.

## Alternatives considered

- **Keep graph promotion-only**: rejected because it creates the observed
  cold-start deadlock and discards the system's best available knowledge.
- **Lower the promotion gate until something promotes**: rejected. That risks
  converting weak positive evidence into overconfident primitives.
- **Add more detectors first**: rejected as insufficient. A larger finite
  signal space can still exhaust without producing a map.
- **Treat falsifications only as methodology records**: rejected because the
  principal's desired causal map needs contradiction and exclusion structure,
  not just a log of failed tests.
