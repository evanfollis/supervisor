# ADR-0048: Derived research lifecycle and bounded autonomy

Date: 2026-07-12
Status: rejected
Author: workspace executive
References: ADR-0027, ADR-0029, ADR-0038, ADR-0042, ADR-0043, ADR-0044,
ADR-0046, ADR-0047

## Context

The platform has most of the pieces of a rigorous research system: Programmes,
immutable Claims, frozen gates, a generic raw-artifact runner, canon validation,
publication guards, full-fidelity telemetry, and reflection. It does not have a
coherent mechanism that advances a research item through those pieces.

That absence is now load-bearing. The first internal Claim is pre-registered,
but execution, Evidence compilation, Decision, knowledge projection,
consumption, and reflection are still session-directed operations. The
knowledge home accepted by ADR-0044 does not exist. The public site is manually
maintained rather than generated from it. A real-store test hard-codes zero
Evidence, so legitimate progress would first look like a regression.

There is also an explicit contradiction in the accepted architecture.
ADR-0042 correctly forbids the canon emitter from selecting what to emit, but
its structural tripwire scans the entire repository for scheduler and
selection names. ADR-0038 separately authorizes a future downstream pressure
kernel only after review. The result is that the project is expected to become
self-driving while repository-wide guards prohibit the control machinery
required to drive it.

The distinction that was missing is between:

- **operational selection**: choosing the next already-authorized, legal,
  bounded action; and
- **epistemic selection**: choosing a Claim, interpreting Evidence, or deciding
  what is true.

Conflating them either produces an inert lab or gives an orchestrator authority
to manufacture knowledge.

## Decision

### One derived lifecycle view

Synaplex will implement one research-lifecycle controller. Its state is derived
from authoritative artifacts; it does not maintain a parallel mutable truth
store.

For a canon Claim, the controller reconstructs these states:

1. `preregistered` — Claim and every frozen gate exist and validate;
2. `ready` — methodology log and probe transition exist and the declared
   executor is available;
3. `running` — a run manifest exists with incomplete work;
4. `observed` — raw artifacts and their hashes are complete;
5. `evidenced` — every declared observation has a resolving Evidence envelope;
6. `decided` — a terminal, validator-passing Decision disposes the Claim;
7. `projected` — a reconstructible knowledge invariant cites that Decision;
8. `consumed` — at least one declared pod records consumption or reasoned
   refusal; and
9. `reflected` — a reflection receipt cites the completed chain and records
   reflector model-state provenance.

Intermediate and failed states are first-class: `blocked`, `aborted`,
`inconclusive`, and `superseded` must retain their reason and source pointers.
The controller exposes `status`, `next`, and `run` commands. `status` explains
how the state was derived. `next` returns the next legal transition and every
blocking condition. `run` may perform only transitions authorized below.

No lifecycle phase is copied onto the immutable Claim. No second status file is
authoritative. Cached indexes are rebuildable projections.

### Control is not authority

The controller may choose among legal transitions for an already-authorized
Claim. It may not:

- derive a canon Claim directly from Programme prose;
- change a Claim, frozen gate, methodology, population, threshold, or oracle;
- choose Evidence polarity through an undeclared heuristic;
- omit contradictory or failed observations;
- decide a Claim through free-form orchestration judgment; or
- publish a result without a validator-passing terminal Decision.

ADR-0042's anti-selection invariant is narrowed to the canon emission boundary:
emitters serialize, validate, and append caller-selected envelopes and never
select their content. The repository-wide name blacklist is superseded. A
research controller may select the next legal transition, but scientific
selection must live in a separately reviewable compiler or adjudicator bound by
the pre-registration.

### Compilers and adjudicators

Raw execution remains epistemically neutral. A runner produces immutable,
hash-addressed artifacts and a run manifest; it does not emit Evidence.

An Evidence compiler may emit Evidence automatically only when the mapping from
run artifacts to Evidence fields, polarity, and observation time is fully
specified by the hash-bound methodology and mechanically testable. Missing,
aborted, malformed, or ambiguous observations remain neutral or inconclusive;
they are never silently dropped or converted into contradiction.

A Decision adjudicator may emit a terminal Decision automatically only when:

- the Claim's frozen gate contains the complete decision rule;
- all expected Evidence is present or explicitly accounted for;
- the result follows deterministically from that rule;
- all contradictory Evidence is cited and addressed; and
- canon validation succeeds against the complete store view.

If interpretation requires open-ended model judgment, the controller emits a
`decision_pending` artifact instead. Model-assisted criticism uses the
Claude/Codex subscription pool, preserves full transcripts and model state, and
cannot itself bypass the deterministic or reviewed Decision boundary.

### Autonomy tiers

- **Tier A — automatic:** read-only observation of declared targets; local
  fixture execution; retry/resume; hashing; integrity checks; deterministic
  Evidence compilation; deterministic adjudication; public-safe projection;
  consumption checks; telemetry; reflection.
- **Tier B — automatic proposal, reviewed authority:** new Claims from
  Programmes, non-deterministic Evidence interpretation, model-judged Decisions,
  changes to research policy, and new public narrative.
- **Tier C — principal authority:** metered spend, new external dependencies,
  credentials, irreversible third-party actions, privacy-boundary changes,
  deliberate impairment of a live service, and constitutional policy.

Capacity exhaustion is operational backpressure, not a credential request.
Claude and Codex subscription CLIs fail over per ADR-0036. If both are blocked,
the lifecycle records `blocked` with the next eligible retry time and resumes
without changing scientific state.

### Projection and consumption

Implement the ADR-0044 knowledge home at `projects/synaplex/knowledge/` as a
small versioned file contract plus deterministic builder. An invariant is
generated only from validator-passing Decisions and must record stable id,
statement, lifecycle interval, Decision ids, supersession, consumers, and last
pressure-test time. Deleting the projection and rebuilding it from canon and
receipts must reproduce the same semantic digest.

The public Synaplex site reads a redacted static projection. Command reads the
same public contract plus private operational overlays. Neither surface derives
research conclusions independently.

Consumption is an explicit receipt containing invariant id and digest, consumer,
action (`consumed` or `refused`), reason, timestamp, and resulting change pointer
when applicable. Silent copying is not consumption.

### Telemetry and self-measurement

Every attempted transition emits a nonblocking operational event with research
id, from/to state, status, artifact pointers, executor version, provider/model
when used, latency, retry/fallback state, and exposed or honest token counts.
Full native transcripts and artifacts remain durable off the hot path per
ADR-0043. Canon, Decision, redaction, and publication checks remain fail-closed.

The controller reports its own research throughput and epistemic hygiene:

- time in each lifecycle state;
- blocked and resumed transitions;
- completed, falsified, killed, inconclusive, and superseded Claims;
- pre-registration violations refused;
- Evidence coverage and missing-observation rate;
- replication and pressure-test age;
- projection drift and consumption latency; and
- model/provider fallback and capacity effects.

These metrics describe the lab. They do not become a reward function that
prefers positive results, more Claims, or faster Decisions.

## First vertical slice

The existing artifact-coherence transfer Claim is the first controller-owned
case. The implementation must:

1. remove the unused `anthropic` SDK dependency and stale provider/phase prose;
2. replace fixed real-store counts with lifecycle invariants that preserve the
   withdrawn vendor route while allowing legitimate new Evidence;
3. execute the pre-registered read-only launchpad-lint browser schedule without
   modifying the service;
4. preserve the raw run manifest, browser artifacts, timestamps, hashes, and
   diagnostic liveness separately;
5. compile the bounded Evidence set and adjudicate only what the N=1,
   predicate-false Claim permits;
6. materialize and reproducibly rebuild the resulting scoped invariant if and
   only if the Decision promotes it;
7. generate the public-safe projection and one pod consumption or refusal
   receipt; and
8. record the final reflection with model-state provenance.

An inconclusive or falsifying observation is a successful loop completion. A
clean result may support only the launchpad-lint-scoped prediction; it cannot
create a cross-service invariant.

## Consequences

- The lab becomes capable of advancing obvious, safe research work without
  session-by-session handholding.
- Scientific authority remains narrower than operational autonomy.
- One derived lifecycle replaces scattered status prose and prevents duplicate
  orchestrators from becoming competing truth sources.
- The old repository-wide anti-selection tripwire is acknowledged as an
  over-broad scaffold and narrowed instead of bypassed with renamed functions.
- Speed comes from automatic safe transitions, negative-result acceptance,
  resumability, and explicit blocked states—not from weakening epistemic labels.

## Alternatives considered

- **Let the canon emitter drive the loop.** Rejected: it combines mechanism and
  authority and recreates the campaign-kernel failure.
- **Keep every transition session-initiated.** Rejected: rigorous components
  remain inert and the principal becomes the scheduler.
- **Store lifecycle state in a new database.** Rejected: duplicates state already
  derivable from canon, runs, projections, and receipts before query pressure
  justifies another system.
- **Use an LLM agent as the state machine.** Rejected: free-form judgment is not
  a replayable transition contract. Models may criticize or propose within the
  typed lifecycle, not replace it.
- **Optimize for publication volume or positive findings.** Rejected: it creates
  Goodhart pressure against inconclusive and falsifying outcomes.

## Adversarial review

Rejected by opposing-model review on 2026-07-12. The proposal is preserved
rather than rewritten because its failure is useful architecture evidence.

The review found:

- determinism does not confer epistemic authority, and automatic deterministic
  adjudication would still decide that a Claim had been answered;
- the current anti-kernel guard does not ban generic scheduler names and would
  not block a `status` / `next` / `run` lifecycle module as proposed, so the
  claimed need to narrow it was false;
- the first vertical slice fails its own automatic-adjudication precondition:
  frozen gate `5273e9a31e92f6c3` carries thresholds but no complete decision
  rule or mechanical attribution oracle;
- `ready` is not currently derivable because no methodology-log or probe-entry
  event exists, and no browser executor exists;
- the proposed run declarations would become an unnamed parallel input store;
- `Tier A/B/C` collides with ADR-0014's existing OS-enforced writable-surface
  vocabulary; and
- nine lifecycle states, four terminal states, three autonomy tiers, eight
  metrics, a compiler, adjudicator, projector, and receipt format are premature
  framework construction around one N=1 Claim.

The review verdict was: build the browser executor, run the three samples, and
review the result. Instrument the first complete cycle, then let repeated real
friction reveal the smallest automation contract.
