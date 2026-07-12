# ADR-0041: A canon emission path for the synaplex lab (corrected)

Date: 2026-07-12
Status: **rejected — superseded-by-0042**
Accepted: — (never accepted)
Rejected: 2026-07-12, executive (general), after cross-agent adversarial review
Author: executive (general), 2026-07-12
Supersedes: ADR-0040 (rejected)
References: ADR-0038 (programmes as discovery plane), ADR-0029 (five-layer pipeline; L2 extraction deferred), ADR-0027 (synaplex is the system), workspace rule S1-P3 (two write paths to one store)
Review artifact: `supervisor/.reviews/adr-0040-codex-2026-07-12T03-30Z.md`

> **REJECTED. Confers no authorization. Do not implement against this document.**
> Read **ADR-0042**, which carries forward everything here that survived review.

## Review verdict (2026-07-12, round 2)

This ADR fixed ADR-0040's scope error and then made a worse one of its own: it
resolved the Policy conflict with governance constraints **canon cannot express.**

**Falsified — blocking:**

1. **`class: operational` is self-defeating.** `policy.md` §Classes defines operational
   as "Agent-mutable within constitutional ceilings," amendable via
   `Decision(kind=amend_policy)` citing Evidence. That is precisely the post-hoc
   flexibility pre-registration exists to close. An operational Policy *is* a movable
   gate. `constitutional` does not fit either — it is principal-only and framework-level
   (capital ceilings, kill-switch). **Canon v0.1.0 has two mutability classes and a
   pre-registered eval gate fits neither.**
2. **"`amendment_authority` must not permit loosening the gate" is unwritable.**
   `policy.schema.json` types `amendment_authority` as a nonempty array of principals;
   `ratification_rule.kind` ∈ `{principal_signoff, evidence_threshold, multi_party}`.
   There is no field for "not amendable within this eval," "only via successor Claim," or
   "not after Evidence exists." The ADR mandated a constraint the schema cannot encode.
3. **Pinning `value` alone does not give "zero new degrees of freedom."** `scope`,
   `field_path`, `ratification_rule`, and `rollback_rule` all remain discretionary. Codex's
   sharpest example: `ratification_rule: evidence_threshold` with count `0` — a gate
   "ratified" by no evidence at all. The value would be frozen; the gate *semantics* would
   not be.

**Serious:**

4. The "bounded precedent" limiting supersession to *emission mechanics* is prose. Nothing
   in schema or validator binds it, and a future session can reclassify a frozen item as
   "mechanics" to get out from under it.
5. `rollback_rule` is incoherent for a first-version, never-rollback gate — rollback
   restores the prior version from `provenance`, and there is no prior version. Only
   `rules: []` / `precedence: []` is sane, and this ADR did not require it.
6. "Byte-identical `value`" would have shipped a broken test: the Claim's thresholds contain
   the lexeme `0.80`, which any normal serializer round-trips to `0.8`. The assertion had to
   be canonical-JSON equality, not byte identity.

**The correct conclusion, which this ADR argued against:**

ADR-0041 says the `minItems: 1` constraint is "canon working as designed, not a gap" and
refuses to escalate. That is right — and it hid the real gap. **Canon Policy cannot encode a
frozen, pre-registered, eval-local promotion gate.** *That* is a genuine canon gap, and
project `CLAUDE.md` is explicit: a lab eval that exposes a canon gap escalates to
context-repository; it does not get a local workaround. This ADR built the local workaround
it warned against.

**Survived, and carried into ADR-0042:** Policy is genuinely required for a terminal
Decision. The immutable methodology must not be edited. The id-contract pin
(`sha256(statement.lower())[:16]`) is right. `effective_from < emitted_at` is schema-valid
and is honest late-serialization. Refusing a schema bump for `policies_in_force.minItems` is
correct. The Programme-laundering honesty correction and the behavioral anti-kernel guard are
material improvements over ADR-0040.

## Context

ADR-0040 proposed a minimal emission path for `lab/.canon/`. Cross-agent adversarial
review endorsed the direction and falsified the scope. This ADR carries the direction
forward on corrected foundations. ADR-0040's Context section is re-verified and stands
except where noted below; it is not repeated here.

Three corrections are load-bearing.

### 1. Policy is schema-forced, and the eval's pre-registration collides with canon

`decision.schema.json` requires `policies_in_force` with `minItems: 1`. `canon.md`
validator rule 5 requires the cited Policy version to exist. Canon obligation 7 — "What
policy applied at the time of each Decision?" — is why. **No eval-terminating Decision
can be emitted without a Policy envelope in the store.** ADR-0040 excluded Policy from
scope while claiming its scope was "what it takes to run one evaluation end to end."
Those cannot both hold.

Worse, and missed by both ADR-0040 and the routing handoff:
`lab/evals/memory-systems-v1/methodology.md` — hash-bound to the pre-registered Claim,
`sha256:45916c9f…`, verified reproducing — says under §Related canon objects:

> Policy (eval promotion-gate): declared inline in the Claim's `thresholds`;
> **no separate Policy object for v1**

The eval, as pre-registered, declines to emit the object canon requires its Decision to
cite. `memory-systems-v1` therefore cannot conclude in a schema-valid Decision **no
matter what the emitter does**. This is a defect in the eval, not in the emission path,
and the artifact cannot be repaired — editing it destroys the pre-registration it
documents.

### 2. The id contracts do not diverge

ADR-0040 open question 2 asserted atlas and synaplex use different id contracts and
recommended keeping them separate. Verified false: atlas's
`claim_hash()` = `sha256(claim_canonical(statement))[:16]`, with `claim_canonical` =
strip → lower → collapse whitespace → strip trailing `[.!?,]`, returns
**`b7ff216f4eec6e58`** on the synaplex Claim's statement — the existing envelope's id,
exactly. Same hash family, same truncation, same lowercase; atlas's normalization is a
strict refinement. The two stores are genuinely separate (`atlas/.canon/` vs
`synaplex/lab/.canon/`, different `instance_id`), so S1-P3 does not bind across them —
but the divergence the ADR proposed to document does not exist for Claims, and settling
an open question on a false premise is how contracts rot.

### 3. The emitter is necessary, not sufficient

ADR-0040 framed the missing emitter as *the* blocker. The eval runner does not exist
either — 0 python files under `lab/`. Both are required before `memory-systems-v1` can
produce Evidence. Naming one blocker as "the" blocker is the overclaim that let this sit
unexecuted for 12 weeks; it is corrected here rather than inherited.

## Decision

Build a minimal, validated, append-only emission path for `lab/.canon/`. Scope: *what it
takes to run one evaluation end to end under canon as it actually is* — which is one
envelope type more than ADR-0040 believed.

### In scope

- Emitters for **five** envelope types: `Claim`, `Evidence`, `Decision`,
  `EventLogEntry`, and **`Policy`**. Policy is not an expansion of ambition; it is a
  dependency of `Decision` that ADR-0040 missed. Not Promotion, not Realization.
- **One id contract, in one module, pinned by a test** asserting `b7ff216f4eec6e58`
  reproduces. The contract is `sha256(statement.lower())[:16]` — ADR-0040's
  recommendation (a). This is the S1-P3 obligation: the first programmatic writer to a
  store reconciles with what is already there.
- **Validation at emission time, refusing to write on violation**, per `canon.md`
  §Validator-level rules ("Adapters that persist envelopes MUST run these checks at
  emission time"). Rules 1, 2, 3, 4, 5, and 7 are in scope and enforced. Rules 6 and 8
  govern fields this path does not emit — the validator must **refuse** if those fields
  appear, not silently pass them.
- **Append-only enforcement**: refuse to overwrite an existing id. Immutability that
  depends on nobody making a mistake is not immutability.
- **`EventLogEntry(canon_violation)` on blocked emission**, per `canon.md` §Blocked
  promotion — a refused write is recorded, not silently dropped.

### The Policy conflict: how it is resolved

The gate's *scientific* content — statement, falsification criteria, thresholds — is
already frozen in the hash-bound Claim. What `methodology.md` got wrong is a statement
about **emission mechanics**: that no Policy object would be created. That plan is
infeasible under canon. Discovering a pre-registered *plan* is impossible is not the same
as changing a pre-registered *hypothesis*.

Therefore:

- **The artifact is not edited.** It stands as the true record of what was planned on
  2026-04-19, including the element of the plan that turned out to be impossible. This
  ADR is the durable, greppable record of what replaces it.
- **A Policy envelope is emitted whose `value` is byte-identical to the Claim's frozen
  `thresholds` object.** Pinned by a test. This is the invariant that makes the
  supersession safe: the Policy introduces **zero** new degrees of freedom in the gate.
  If `value` can drift from `thresholds`, the supersession is a loophole, not a fix.
- `class: operational` — it governs an eval gate, not the platform constitution.
- `issuer: L3:synaplex`.
- `effective_from` = the Claim's `emitted_at` (`2026-04-19T04:25:00Z`), while
  `emitted_at` is the real emission time. The divergence is the point: the record then
  reads *"in force since pre-registration, serialized late,"* which is exactly what
  happened. Backdating `emitted_at` would be a lie; backdating `effective_from` is the
  truth.
- **`amendment_authority` must not permit loosening the gate within this eval.**
  Amending the gate requires a successor Claim. A Policy whose amendment authority lets
  a later session move the threshold after Evidence exists would re-open, through the
  governance fields, exactly the post-hoc flexibility pre-registration exists to close.

This is the narrowest resolution that lets the eval conclude. The bounded precedent, and
its limits, are stated under Consequences — it must not be read as a general licence.

### Out of scope — explicitly

- **No revival of `lab/campaign`.** No Campaign object, scheduler, outcome map, publish
  gate, or manifest. ADR-0038 §Cleanup governs. A downstream pressure kernel is a
  separate decision with its own safety requirements (ADR-0038 lists them), and this ADR
  must not be read as a step toward one.
- **No canon schema bump.** L1 stays frozen at v0.1.0. The `minItems: 1` on
  `policies_in_force` is canon working as designed, not a gap — a Decision governed by no
  policy is unanswerable in canon's model. Escalating it to context-repository would be a
  workaround dressed as governance.
- **No automation.** Nothing in intake, reasoning, or the reflection loop may invoke the
  emitter. Emission is session-initiated and reviewed. An emitter on a timer is a machine
  for manufacturing canon.
- **No runner.** Executing `memory-systems-v1` is separate engineering under a separate
  authorization.
- **No rival Claim.** The control-arm remedy in handoff
  `synaplex-memory-systems-v1-missing-control-arm-2026-07-12T02-05Z` is a *use* of this
  path, not a grant of it. See Sequencing.

### The anti-kernel guard is behavioral, not a path check

ADR-0040's only mechanical guard was "no file under `lab/campaign/` exists." That binds a
path; the same kernel rebuilt at `lab/pressure/` satisfies it. The real invariant:

> **The emitter serializes, validates, and writes. It never selects what to emit.**

No code in the emission path may compute *which* Claim to register, *which* Decision to
reach, or *when* to emit. Those are session judgments, reviewed. Inputs come from the
caller; the emitter's only decisions are *"is this valid"* and *"does this already
exist."* The distance from "emit a Decision" to "compute which Decision to emit" is short
and downhill, and it is the exact slope `15edd38` slid down.

### ADR-0038 alignment — and one guarantee we do not have

Three constraints are mechanically enforceable and must be enforced:

1. **The emitter has no knowledge of Programmes.** It takes no Programme path, reads no
   Programme file, and cannot be invoked "by" a Programme.
2. **Write-side path refusal.** Refuse to emit any envelope whose
   `ArtifactPointer.uri`, `sources[*]`, or any other field points into
   `reasoning/programmes/`. This is new capability: `check_programmes.py` catches path
   citation at *scan* time, after the bad envelope already exists in an append-only
   store. Refusing at write time makes the violation impossible rather than detectable.
3. **No provenance slot.** Per ADR-0038 authority contract §4, that a Programme led to a
   Claim is recorded in the Programme's graduation ledger, never in the Claim envelope.

The fourth is **not mechanically enforceable, and this ADR will not pretend otherwise.**
ADR-0040 claimed all four were. ADR-0038 §Reference direction says the opposite in terms:
*"The grep/path guard can catch path citation laundering. It cannot catch copied content.
The copy/re-ingest ban is therefore a reflection-review obligation, not a fully mechanical
guarantee."* An emitter that hash-pins an artifact will pin Programme prose copied into
that artifact without any `reasoning/programmes/` path appearing. That channel stays open,
it is covered by reflection review, and the emitter must not advertise a guarantee it does
not provide.

## The id contract

Pin `sha256(statement.lower())[:16]`, and **record that atlas's stricter derivation
reproduces the same id** — the contracts are compatible today; they differ only in
normalization strictness, not hash family.

Do **not** vendor atlas's `claim_canonical()` into synaplex. Copying a repo-local helper
across a repo boundary with no shared test surface creates a second copy of a contract
that can drift silently — the exact class S1-P3 names — and L2 `discovery-runtime`
extraction stays deferred per ADR-0029 until synaplex has actually executed several evals.
Extracting from one working example and one that has never run would bake in
incompatibilities we have not discovered yet.

Two consequences to hold explicitly:

- The contract is **case-insensitive**: two Claims differing only in case collide. This is
  made safe by *refusing to write on collision*, loudly, not by changing the hash. A
  refusal is recoverable; a silent overwrite of a pre-registration is not.
- Evidence, Decision, and EventLogEntry ids **do** genuinely diverge from atlas (atlas uses
  domain-native ids like `dec-<hash>-kill`, and 12-char evidence ids against 16-char claim
  ids). Nobody may later write a cross-instance join assuming a shared scheme. When L2
  extraction happens, Claims converge cheaply and these do not.

## Sequencing (what this ADR does and does not unblock)

1. **Now:** build the emission path. Its immediate legitimate consumers exist and precede
   the runner — the probe-entry `EventLogEntry(phase_transition)` + `methodology_log` that
   `canon.md` §Phase invariants requires on probe entry, and the Policy envelope above.
2. **Then:** adversarial review (cross-agent — synaplex is a Claude session, so route to
   Codex), per project `CLAUDE.md`, which requires it for canon-adjacent changes.
3. **Then, separately authorized:** the control-arm rival Claim. Its pre-registration
   window is open only while zero Evidence exists and closes on the first run — but with no
   runner, nothing is closing it imminently. It is emitted through this path once
   authorized, not rushed ahead of a reviewed emitter. Hand-authoring it is what produced
   the drift being cleaned up here.
4. **Then, separately authorized:** the runner.

## The methodology id-drift is documented, not repaired, and not reconciled in canon

`methodology.md` cites Claim `memory-systems-v1-h1` at two paths that do not exist; the
real id is `b7ff216f4eec6e58`. **This is not a canon violation.** Validator rule 7 requires
`ArtifactPointer.content_hash` to reproduce from the artifact — it does. The stale label is
prose *inside* the artifact, not a canon reference. Canon is self-consistent.

Therefore: do not repair the artifact (it would break the pre-registration), and do not
manufacture a reconciliation envelope. An earlier draft of this review proposed recording
the mapping in `EventLogEntry(methodology_log).summary`; that was withdrawn under review —
`summary` is free-form narrative, and putting audit-load-bearing content there makes audit
depend on prose parsing and smuggles a schema gap past the L1 freeze. The drift is recorded
in `CURRENT_STATE.md` and project `CLAUDE.md`, which is where readers look. That is
sufficient and it is where it stays.

## Acceptance criteria

1. Id-contract module with a test asserting `b7ff216f4eec6e58` reproduces under
   `sha256(statement.lower())[:16]`.
2. Emission-time validation enforcing `canon.md` validator rules 1, 2, 3, 4, 5, 7 — refusing
   the write on violation. Rules 6 and 8 refuse rather than silently pass.
3. Append-only enforcement, with a test proving an overwrite attempt raises **and leaves the
   envelope on disk byte-unmodified**.
4. Write-side Programme-path refusal, with a test. Documented as *not* covering copied
   content.
5. A Policy envelope for the `memory-systems-v1` promotion gate, with a test asserting its
   `value` is byte-identical to the Claim's frozen `thresholds`, `effective_from` equals the
   Claim's `emitted_at`, and its `amendment_authority` does not permit in-eval gate changes.
6. A test asserting the emitter does not select what to emit: no scheduler, no outcome map,
   no rival generation, no code path that computes which Decision to reach — **anywhere in
   the repo**, not merely under `lab/campaign/`.
7. `EventLogEntry(canon_violation)` emitted on every refused write.
8. `python -m integrity` and `reasoning/check_programmes.py` still clean.
9. Cross-agent adversarial review before merge (route to Codex).
10. No file under `lab/campaign/` exists, and no equivalent kernel exists under any other
    path.

## Consequences

- The lab gains the ability to write canon. This is the highest-consequence change
  available in this repo: an emitter is the thing that makes an append-only, hash-pinned
  store *writable*, and therefore corruptible. The scrutiny it deserves is not proportional
  to the amount of code.
- `memory-systems-v1` becomes concludable — but is **still blocked** on the runner and on
  the missing control arm. This ADR removes one of three blockers and says so plainly.
- **A bounded precedent is set:** where an immutable pre-registration records an *emission
  plan* that canon does not permit, the plan may be superseded by a durable decision, the
  artifact is never edited, and the superseding object must introduce **zero** new degrees
  of freedom in the frozen scientific content — enforced by a test, not by intent. This
  licence extends to nothing else. It does not permit revisiting a statement, a
  falsification criterion, or a threshold. A future session citing this paragraph to loosen
  a gate is misreading it.
- ADR-0040 is rejected, not silently dropped. Its analysis is preserved in git and in the
  review artifact; its scope is not authoritative.
- The status vocabulary in `supervisor/CLAUDE.md` §Decisions
  (`proposed | accepted | superseded-by-NNNN`) has no way to record a rejected proposal.
  Accepting this ADR authorizes amending it to
  `proposed | accepted | rejected | superseded-by-NNNN`. A governance surface that can only
  record approvals is not a governance surface.

## Alternatives considered

- **Accept ADR-0040 with the corrections pencilled into the review.** Rejected. Its central
  scope claim is provably false and one supporting premise is factually wrong. A decision of
  record whose reasoning does not support its conclusion is worse than no decision — the next
  session reads the conclusion, not the review.
- **Emit a successor Claim for `memory-systems-v1` that includes the Policy.** Rejected. It
  retires a pre-registration whose scientific content is sound, and the control-arm handoff
  independently argues against a successor for the same reason. Serializing an
  already-frozen gate is strictly less invasive than re-registering the hypothesis.
- **Escalate `policies_in_force: minItems: 1` to context-repository as a canon gap.**
  Rejected. Canon obligation 7 is deliberate. The gap is in synaplex's pre-registration, not
  in canon, and escalating it would be a local workaround wearing governance clothes.
- **Converge synaplex's id contract on atlas's `claim_canonical()`.** Rejected under review.
  It reproduces the existing envelope, but vendoring a repo-local helper across a repo
  boundary with no shared test creates a second drifting copy of the contract, and premature
  L2 extraction would generalize from one working example and one that has never run.
- **Do nothing.** Still a real option, and still costed honestly: the lab cannot write,
  `memory-systems-v1` stays parked, and the "publication + evaluation lab" half of ADR-0027
  remains aspirational. A deliberate pause is fine. A pause by omission is what produced the
  last 12 weeks.
