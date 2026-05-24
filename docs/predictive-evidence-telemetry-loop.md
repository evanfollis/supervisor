# Predictive Evidence Telemetry Loop

Updated: 2026-05-24
Owner: executive

## Purpose

The workspace needs telemetry that improves judgment rather than producing
semantic theater. For passive-income candidates, especially stochastic market
underwriting systems, every meaningful action or non-action should leave an
auditable prediction row before the outcome is known, followed by observations,
scoring, conclusions, and lessons after the item closes.

The objective is not to prove the system was smart. The objective is to create
enough high-quality, time-indexed evidence that future agents can improve
pricing, ranking, action thresholds, and kill decisions.

## Core Rule

Predictions are immutable once recorded. Observations, conclusions, and lessons
are appended later. Retrospective edits must create a superseding record, not
rewrite the original prediction.

## Ledger Row Shape

Each row should include:

- `row_id`
- `candidate_id`
- `market_surface`
- `item_id`
- `item_snapshot_ref`
- `snapshot_time`
- `source_terms_status`
- `agent_run_id`
- `model_id`
- `tool_versions`
- `prompt_or_policy_ref`
- `action_tier` (`observe_only`, `paper_trade`, `pilot`, `live_capital`)
- `allowed_actions`
- `blocked_actions`
- `hypothesis`
- `prediction_targets`
- `prediction_values`
- `confidence_or_distribution`
- `decision_thresholds`
- `expected_value_metric`
- `risk_budget`
- `reasoning_summary`
- `evidence_refs`
- `causal_assumptions`
- `counterfactuals`
- `known_unknowns`
- `recommended_action`
- `actual_action`
- `close_time`
- `outcome_observations`
- `score`
- `error_attribution`
- `lesson`
- `future_policy_suggestion`
- `supersedes`
- `superseded_by`

Reasoning summaries should be concise, structured, and scoreable. Do not store
unbounded chain-of-thought style prose as if it were evidence. Store the
decision-relevant premises, assumptions, data references, uncertainty, and
action policy.

## Prediction Targets

For recommerce underwriting, useful targets include:

- final hammer price
- whether final hammer price stays below recommended max bid
- all-in landed cost estimate
- expected recovery estimate
- estimated margin after all reserves
- category liquidity
- sell-through probability
- source/data-quality failure
- whether the item should be ignored, watched, paper-bid, or later bid

For data/API and agent-tooling products, useful targets include:

- first passive paid event probability by date
- activation probability by channel
- repeat-use probability
- support burden
- cost per fulfilled request
- conversion by source surface
- failure rate by model/tool/policy version

## Scoring

Use metrics that match the prediction:

- price estimates: absolute error, percentage error, signed bias, and rank error
- probability estimates: Brier score, log loss, and calibration buckets
- ranking: precision at top-k, recall at threshold, opportunity cost, and regret
- margin: expected edge vs observed or best-available proxy edge after fees
- system behavior: cost per row, retry rate, tool failure rate, latency, and
  human-intervention count
- portfolio value: first passive paid event, repeat paid events, retained usage,
  and net revenue after platform and fulfillment costs

If an outcome cannot be observed directly, label it as proxy evidence. Do not
pretend an inferred resale outcome is the same as a verified resale outcome.

## Temporal Causal Map

The system should maintain a temporal reasoning graph, not a static explanation
tree. Nodes are variables, observations, assumptions, items, categories,
markets, policies, and outcomes. Edges are claimed relationships with:

- timestamp
- source row or review
- confidence
- regime or context
- direction of effect
- evidence type
- known confounders
- review status

Call these causal hypotheses until intervention or strong natural-experiment
evidence supports stronger language. Most early edges will be provisional:
"freight uncertainty appears to reduce edge quality" is acceptable; "freight
uncertainty causes losses" is usually not.

## Review After Close

Every closed item should receive a post-close review with:

- what the system predicted
- what happened
- where the gap came from
- whether the action policy would have changed with better information
- whether the miss was data, model, tool, policy, market-regime, or execution
- what feature, rule, source, or guardrail should change
- what should remain unchanged despite the outcome
- one concrete suggestion to future agents

The review must separate luck from process quality. A profitable paper outcome
can still be a bad decision if the reasoning was wrong. A losing paper outcome
can still improve the system if the uncertainty was honestly priced and the
lesson is reusable.

## Anti-Theater Constraints

- No unscored "insights" without an attached future prediction or policy change.
- No confidence updates without naming the evidence that changed confidence.
- No retrospective movement of thresholds after the outcome is known.
- No narrative-only success claims when the metric is margin, conversion, cost,
  or risk.
- No aggregating across categories or regimes until the row count and
  distribution justify it.
- No calling a loop self-improving unless it changes future predictions,
  thresholds, source selection, or action policy.

## Agentic Systems Baseline

As of Q2 2026, production agent systems have better tracing, sandboxing,
handoff, and durable-execution primitives than earlier systems, but reliability
still depends on instrumentation, source control, and outcome scoring. Treat
agent traces as operational evidence, not as proof of reasoning correctness.

Minimum telemetry for agent runs:

- LLM generations
- tool calls
- handoffs
- guardrail outcomes
- custom decision events
- retrieved references
- source snapshots or hashes
- retry/cost amplification
- model and prompt/policy versions
- sandbox or environment snapshot where relevant
- final artifact refs

Hidden orchestration cost, retries, tool failures, and ungoverned MCP/tool
endpoints are first-class risks. They should be tracked alongside market
prediction quality.

## Action Tiers

Use staged evidence gates:

- `observe_only`: collect public or licensed observations; no recommendation
- `paper_trade`: produce recommendations before outcomes; no capital
- `pilot`: limited user-facing feed or subscription; no inventory/capital
- `live_capital`: real capital or inventory exposure; requires separate
  principal decision

For Intimidation Market Arbitrage, the authorized default is `paper_trade` at
most. Live buying, brokerage, inventory handling, freight coordination, or
manual resale is out of scope until explicitly approved.
