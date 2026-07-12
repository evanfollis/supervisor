# ADR-0049: Complete one instrumented cycle before orchestration

Date: 2026-07-12
Status: accepted
Author: workspace executive
References: ADR-0036, ADR-0038, ADR-0042, ADR-0043, ADR-0044, ADR-0046,
ADR-0047; rejected ADR-0048

## Context

The principal wants a high-octane, self-driving scientific research lab. The
platform currently has zero completed Synaplex Evidence cycles. ADR-0048 tried
to design the eventual controller before the first cycle and was rejected by
opposing-model review as premature framework construction.

That rejection does not weaken the autonomy objective. It defines the honest
path to it: instrument one complete cycle, observe where judgment and friction
actually occur, and automate only transitions that prove repetitive and
mechanical.

The current implementation also contains immediate contradictions:

- `anthropic` remains an unused package dependency after metered model paths
  were removed;
- canon documentation still says Decision and Policy support is blocked even
  though emitters and real Decision envelopes exist;
- the accepted `projects/synaplex/knowledge/` home does not exist;
- the active study has no browser executor; and
- a real-store test hard-codes zero Evidence, so a legitimate observation would
  fail CI before it could be reviewed.

These are architecture defects, not cleanup trivia.

## Decision

### Finish the current study without a new controller

The artifact-coherence transfer study is completed as one attended,
fully-instrumented vertical slice. Do not add a scheduler, research database,
generic lifecycle framework, automatic Claim generation, automatic canon
emission, or automatic Decision adjudication in this cycle.

The sequence is:

1. verify the existing Claim, frozen gate, methodology hash, and subject scope;
2. emit the required methodology-log and probe-entry events through the reviewed
   canon emitter before observing the subject;
3. execute exactly the pre-registered read-only browser schedule against
   launchpad-lint without build, deploy, restart, state mutation, or deliberate
   impairment;
4. preserve raw browser, HTTP, liveness, source identity, timestamp, and hash
   artifacts in an idempotent run directory;
5. review the complete raw set and emit only Evidence that the methodology
   supports, with ambiguous attribution labeled inconclusive rather than forced;
6. produce an opposing-model methodological review;
7. emit a bounded Decision through the existing validator, citing every frozen
   gate and every relevant Evidence item;
8. if the Decision supports a reusable scoped statement, materialize it through
   the ADR-0044 knowledge projection; otherwise record plainly why no invariant
   is justified and keep the full loop open;
9. generate the public-safe projection from that knowledge record, never by
   independently interpreting raw Evidence;
10. obtain one real pod consumption or reasoned-refusal receipt; and
11. run reflection and record the reflector's provider, model, reasoning effort,
   token state when exposed, and source pointers.

Negative, falsifying, killed, or inconclusive outcomes are successful research
outcomes. They do not justify manufacturing an invariant merely to satisfy the
shape of ADR-0044's acceptance test.

### Correct the substrate before observation

Before probe entry:

- remove the unused `anthropic` dependency and any stale live documentation
  that describes a metered scorer or blocked Decision phase;
- retain the withdrawn vendor study verbatim as historical lineage;
- replace global fixed-count assertions with semantic invariants: withdrawn
  Claims remain killed with zero Evidence, all envelopes validate, active Claims
  may progress only through legal canon transitions, and publication remains
  Decision-gated;
- implement a study-specific browser executor and raw-artifact schema under the
  active study directory, not a generic framework;
- prove idempotent resume and prove aborted samples cannot become observations;
  and
- preserve complete telemetry off the hot path with the secured spool.

The current anti-kernel guard remains intact. ADR-0042's no-automatic-emission
rule remains intact for this cycle. Existing Decision and Policy emitters are
acknowledged as landed capability after canon v0.2.0 resolved the original
Policy gap; their stale module and guard documentation must be corrected, not
used as permission for automated adjudication.

### Implement only the minimum knowledge contract

Create `projects/synaplex/knowledge/` only when the Decision boundary is ready to
be exercised. The v0 contract is file-backed and reconstructible per ADR-0044.
It contains:

- a schema for an invariant and a consumption/refusal receipt;
- a deterministic builder from validator-passing Decisions and explicit receipt
  inputs;
- a semantic digest and rebuild test; and
- a public redaction/projection test.

Do not add a graph, database, service, mutable status registry, or retrieval
layer. Empty infrastructure may be built and tested, but fabricated knowledge
may not be inserted.

### Autonomy ratchet

After the first cycle, reflection must classify every transition as:

- mechanical and safely repeatable;
- judgment-bearing but reviewable;
- externally consequential; or
- unnecessary ceremony.

Only mechanical transitions that have succeeded in at least two real cycles may
be proposed for unattended execution. Canon emission and scientific Decision
remain reviewed until a later accepted ADR demonstrates, from those cycles,
that a narrower automatic compiler or adjudicator is both useful and
epistemically safe.

The eventual research controller, if evidence justifies one, must derive state
from existing artifacts and must not duplicate supervisor tick state, project
front doors, canon phase, or run manifests.

## Consequences

- The platform moves immediately instead of designing a speculative lab OS.
- The first loop becomes empirical evidence about the research machinery
  itself.
- The autonomy objective remains, but automation is earned by observed
  repetition rather than asserted from architectural taste.
- The principal is not made the routine scheduler: the attended Synaplex
  project session owns this cycle and escalates only genuine authority
  boundaries.
- A full loop may remain incomplete after this study if the evidence does not
  justify a reusable invariant. That limitation is reported, not papered over.

## Alternatives considered

- **Accept ADR-0048 with amendments.** Rejected: its framework shape remains
  disproportionate to the empirical base.
- **Run the observation immediately without substrate cleanup.** Rejected: CI
  currently treats legitimate Evidence as failure and the executor does not
  exist.
- **Keep discussing self-driving architecture before running anything.**
  Rejected: it repeats the platform's current failure mode.

## Adversarial review

Accepted as the minimal response to the opposing Claude Opus review of
ADR-0048. That review inspected the live canon store, guard, rejected campaign
kernel, referenced ADRs, and current study gate. Its binding correction was to
run and instrument the three pre-registered samples before authorizing a generic
controller or automatic epistemic writes.
