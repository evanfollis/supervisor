# ADR-0019: Measurement systems co-located with their subject must discriminate self-traffic

Date: 2026-04-17
Status: accepted

## Context

The 2026-04-17T15:23Z cross-cutting synthesis surfaced a workspace-wide failure
class: measurement systems are conflating automated/internal traffic with real
signal.

Concrete instances:

- **Valuation preflight watcher** logged 161 of 162 sessions with UA
  `Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36` and `latencyMs: 0–1`.
  External HTTP round-trips cannot complete in 0–1 ms; this is self-generated
  loopback/localhost traffic (smoke test, MCP inspector, or cron check). The
  watcher's `IGNORE_RE` has no latency floor, so 161 self-traffic events were
  classified `REAL-USER`. The single genuinely external signal
  (`curl/8.5.0`, `latencyMs: 3`) was diluted into noise.
- **Command telemetry** (now fixed in `22e69e6`) emitted `executive.thread_read`
  at 99.8% of event volume — all self-generated polling. This was addressed at
  source (stop emitting) rather than by discrimination.

S1-P2 (`sourceType`) solved the telemetry side of this problem. Watchers and
probes have no equivalent contract. The general principle — any measurement
system running on the same host as its subject needs an explicit gate to
exclude self-traffic — has not been written down anywhere.

## Decision

Amend `/opt/workspace/CLAUDE.md` §Architecture Governance (after the
`sourceType` bullet) with a workspace-wide rule:

> **Measurement systems co-located with their subject must discriminate
> self-generated traffic.** A watcher, probe, or monitor running on the same
> host as the service it observes must apply at least one of: latency floor
> (sub-2ms round-trips are loopback on the local host), `sourceType` /
> source-class tagging, or explicit IGNORE patterns for known automated UAs
> and internal callers. Counting self-traffic as organic signal is worse
> than having no measurement — it produces false confidence. When in doubt,
> assume localhost traffic is self-generated and require positive evidence
> (novel UA, non-loopback origin, latency consistent with a real network
> path) to classify an event as external.

This is a guidance rule, not an enforcement mechanism. Projects with
co-located measurement opt in by applying it to their measurement code:

- skillfoundry-valuation preflight watcher: add latency-floor filter to
  `IGNORE_RE` logic; investigate the source of the `Mozilla/0ms` sessions.
- command telemetry: already addressed via `sourceType` per S1-P2.
- atlas: not yet co-located with a live exchange — the rule applies once
  the live path is in use.

## Consequences

**Enables:**

- Genuine external signal becomes distinguishable from self-traffic at
  ingestion, not downstream in analytics.
- Cross-project consistency: the same discrimination contract applies
  regardless of which project emits.
- The rule is reusable for future measurement surfaces (content-funnel
  attribution from the skillfoundry agentic inbound work, for example,
  inherits this contract).

**Makes harder:**

- Every new watcher or probe has an explicit discrimination step in its
  design. This is a small friction at write-time that pays back at
  analysis-time.
- Retrofitting existing watchers requires touching their classification
  logic. The valuation watcher retrofit is the first test case.

**Foreclosed:**

- The "measure everything, filter later" pattern. Downstream filters
  cannot reliably recover the self/external signal distinction once the
  events are indistinguishable in storage.

## Alternatives considered

- **Project-specific fix for valuation only.** Rejected: the failure class
  is workspace-wide (command had the same pattern, atlas will have it
  when live). A project-only fix doesn't prevent the next recurrence.
- **Mandatory `sourceType` on watcher events (like telemetry).** Overreach:
  `sourceType` is a telemetry contract with specific values (`user`,
  `system`, `smoke`, `cron`); watcher events may need other discriminators
  (latency, UA). The rule mandates the outcome (discrimination), not the
  mechanism.
- **Force all measurement off-host.** Impractical for hobby-scale
  infrastructure and unnecessarily heavyweight. The discrimination rule
  is sufficient.

## Implementation

- `/opt/workspace/CLAUDE.md` §Architecture Governance: add the
  discrimination bullet verbatim as quoted above.
- `/opt/workspace/runtime/.handoff/skillfoundry-valuation-watcher-signal-discrimination-<ts>.md`:
  route to skillfoundry-valuation with the investigation + IGNORE-rule
  retrofit as the deliverable.
- Future watchers/probes: the rule is in effect at design-time, not
  just retrofit.
