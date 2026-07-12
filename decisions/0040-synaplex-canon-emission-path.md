# ADR-0040: A canon emission path for the synaplex lab

Date: 2026-07-12
Status: **proposed**
Accepted: —
Author: synaplex session, 2026-07-12
References: ADR-0038 (programmes as discovery plane), ADR-0027 (synaplex is the system), ADR-0029 (five-layer pipeline), ADR-0019 (self-generated traffic), workspace rule S1-P3 (two write paths to one store)

> **This ADR is a proposal. It is not accepted and confers no authorization.**
> No code may be written against it until an executive/principal acceptance is
> recorded in the `Accepted:` field above. It exists because ADR-0038 §Cleanup is
> explicit that the reverted `lab/campaign` kernel is not authorization for
> building an emission path — so the path needs its own decision, made
> deliberately, rather than arriving as a side effect of some other task.

## Context

The synaplex lab cannot currently execute an evaluation. Not "has not" — *cannot*.

Verified state of `lab/.canon/` as of 2026-07-12:

| | count |
|---|---|
| Claim | 1 (hand-authored, 2026-04-19) |
| Evidence | 0 |
| Decision | 0 |
| EventLogEntry | 0 |
| Policy | 0 |

**No code writes to this store.** `CLAUDE.md` §Structure documented a
`lab/canon_emit.py` and "a small in-repo validator"; neither has ever existed. The
drift was removed in `synaplex@93aa633`. The one Claim in the store was written by
hand.

Three consequences follow, and they compound:

1. **The lab is structurally blocked.** `canon.md` §Phase invariants requires an
   `EventLogEntry(phase_transition)` plus a `methodology_log` entry on probe entry.
   With no emitter, `memory-systems-v1` cannot enter probe, cannot emit Evidence,
   and cannot emit a Decision. It has been pre-registered and unexecuted since
   2026-04-19 — ~12 weeks — and no amount of scheduling fixes that, because the
   blocker is that there is nothing to write with.

2. **The id contract is unenforced and reverse-engineered.** The existing Claim's
   id derives as `sha256(statement.lower())[:16]`. This was recovered by trying
   candidate derivations against the one envelope, not read from a spec. It is
   written down nowhere and asserted by nothing. It is also **case-insensitive**,
   so two Claims whose statements differ only in case collide silently.

3. **Hand-authoring has already produced drift.** `methodology.md` — itself
   hash-bound and immutable — references Claim `memory-systems-v1-h1` at
   `lab/.canon/claims/memory-systems-v1-h1.json`. Neither the id nor the path
   exists; the real id is `b7ff216f4eec6e58`. This is exactly the class of error a
   validated emission path prevents and a human writing JSON does not.

The workspace already has two canon emitters — atlas
(`src/atlas/adapters/discovery/emit.py`) and skillfoundry — and they use a
*different* id contract from synaplex's: they pass through the domain's native id,
where synaplex derives from the statement. That divergence is fine (different
natural keys) but it is currently undocumented, which is precisely the situation
workspace rule S1-P3 exists to prevent.

## Decision (proposed)

Build a minimal, validated, append-only emission path for the synaplex lab canon
store. Its scope is *"what it takes to run one evaluation end to end, and nothing
more."*

### In scope

- Emitters for the four envelope types an eval actually produces: **Claim**,
  **Evidence**, **Decision**, **EventLogEntry**. Not Policy, Promotion, or
  Realization — those land when something needs them.
- **One id contract, in one module, pinned by a test** that asserts the
  pre-existing envelope still reproduces under it. This is the S1-P3 obligation:
  the first programmatic writer to a store must reconcile with what is already
  there.
- **Validation at emission time**, refusing to write on violation. `canon.md`
  §Validator-level rules is explicit: "Adapters that persist envelopes MUST run
  these checks at emission time." Minimum set: `role_declared_at <= emitted_at`;
  `chosen_claim_id ∈ candidate_claims`; set-equality of
  `{chosen} ∪ {rejected_alternatives}` against `candidate_claims`; and
  `ArtifactPointer.content_hash` reproducing from the artifact at `uri`.
- **Append-only enforcement**: refuse to overwrite an existing id. Immutability
  that depends on nobody making a mistake is not immutability.
- **`EventLogEntry(canon_violation)` on blocked emission**, per `canon.md`
  §Blocked promotion — a refused write is recorded, not silently dropped.

### Out of scope — explicitly

- **No revival of `lab/campaign`.** No Campaign object, no pressure scheduler, no
  outcome map, no publish gates, no manifest. ADR-0038 §Cleanup governs; if a
  downstream pressure kernel is ever wanted it is a *separate* decision with its
  own safety requirements, and this ADR must not be read as a step toward one.
- **No canon schema bump.** L1 canon stays frozen at v0.1.0. If an eval exposes a
  canon gap, that escalates through context-repository, not a local workaround.
- **No automation.** Nothing in intake, reasoning, or the reflection loop may
  invoke the emitter. Emission is session-initiated and reviewed. An emitter on a
  timer is a machine for manufacturing canon.

### ADR-0038 alignment (load-bearing, not a formality)

The emission path is the exact surface where Programme content could launder
itself into canon. Four constraints, all mechanically enforceable:

1. **The emitter has no knowledge of Programmes.** It takes no Programme path, reads
   no Programme file, and cannot be invoked "by" a Programme. A draft claim
   graduates because a session decided to emit it through the strict path — the path
   itself never learns where the idea came from.
2. **Write-side laundering guard.** The emitter must *refuse* to emit any envelope
   whose `ArtifactPointer.uri`, `sources[*]`, or any other field points into
   `reasoning/programmes/`. This is new capability, not a restatement:
   `check_programmes.py` catches path citation at *scan* time, after the bad
   envelope already exists in an append-only store. Refusing at write time makes the
   violation impossible rather than detectable.
3. **Provenance stays in the Programme ledger.** Per ADR-0038 authority contract §4,
   the fact that a Programme led to a Claim is recorded in the Programme's graduation
   ledger, never in the Claim envelope. The emitter offers no provenance slot for it.
4. **Graduation carries no privilege.** A claim that came from a Programme is
   validated exactly as strictly as one that did not.

## Open questions requiring a decision (do not let these be settled by default)

1. **The id contract.** Options: (a) adopt `sha256(statement.lower())[:16]` as-is,
   pin it, and make collisions a loud refusal; (b) switch to a case-sensitive
   derivation, accepting that the existing envelope no longer conforms; (c) new
   contract plus a successor Claim retiring the existing one. **Recommendation: (a).**
   Pre-registration immutability outranks contract elegance, and (b) reintroduces the
   two-contracts-one-store problem S1-P3 names. The case-collision hazard is real but
   is made safe by refusing to write on collision rather than by changing the hash.
2. **Relationship to the atlas emitter.** Keep separate (the natural keys genuinely
   differ) or unify? **Recommendation: keep separate, document the divergence in
   canon terms**, so nobody later writes a cross-instance join that assumes a shared
   id scheme. L2 `discovery-runtime` extraction stays deferred per ADR-0029 until
   synaplex has actually executed several evals — extracting before the first eval
   would bake in incompatibilities we have not yet discovered.
3. **First exercise.** Is the first thing emitted through this path the
   control-arm rival Claim for `memory-systems-v1` (see open handoff
   `synaplex-memory-systems-v1-missing-control-arm-2026-07-12T02-05Z`)? That is a
   *separate* authorization: this ADR proposes the path, not any particular use of
   it. Note the timing constraint — registering that rival is only legitimate while
   zero Evidence exists; after the first run it is post-hoc rationalization.

## Risks

- **An emitter is the thing that makes canon writable, therefore corruptible.** The
  entire value of the store is that it is append-only and hash-pinned. Adding a
  writer is the highest-consequence change available in this repo, and it deserves
  more scrutiny than the amount of code implies.
- **Scope creep toward the reverted kernel.** The distance from "emit a Decision"
  to "compute which Decision to emit" is short and downhill. The out-of-scope list
  above is the guardrail; if a future session finds itself wanting a scheduler, that
  is a new ADR, not an extension of this one.
- **Precedent.** `synaplex@15edd38` was agent-initiated infrastructure that assumed
  authorization from a handoff. This ADR exists so the emission path does not repeat
  that, and it must not itself become the thing a later session cites as blanket
  permission.

## Alternatives considered

- **Keep hand-authoring envelopes.** Rejected. It does not survive contact with a
  second envelope, and it has *already* produced an unreproducible id contract and a
  hash-bound methodology that cites a claim id which does not exist. Hand-authoring
  is not the conservative option; it is the option that generated the current drift.
- **Extract atlas's emitter into a shared L2 library first.** Deferred, per ADR-0029:
  L2 extraction waits until synaplex has executed several evals. Doing it now would
  generalize from one working example and one that has never run.
- **Build a full canon validator.** Deferred. Build the subset `canon.md` requires at
  emission time; a general validator is a bigger object with no current consumer.
- **Do nothing.** This is a real option and should be chosen explicitly if chosen.
  Its cost: the lab cannot run, `memory-systems-v1` stays parked indefinitely, and
  the "publication + evaluation lab" half of ADR-0027 remains aspirational. If that
  is acceptable for now, say so — a deliberate pause is fine; a pause by omission is
  what produced the last 12 weeks.

## Acceptance criteria (if accepted)

1. Id contract module with a test asserting `b7ff216f4eec6e58` still reproduces.
2. Emission-time validation refusing writes that violate the canon rules named above.
3. Append-only enforcement with a test proving an overwrite attempt raises and leaves
   the envelope on disk unmodified.
4. Write-side Programme-path refusal, with a test.
5. `python -m integrity` and `reasoning/check_programmes.py` still clean.
6. Adversarial review before merge (project CLAUDE.md requires it for canon-adjacent
   changes).
7. No file under `lab/campaign/` exists.
