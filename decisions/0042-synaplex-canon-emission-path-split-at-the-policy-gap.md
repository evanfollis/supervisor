# ADR-0042: The synaplex canon emission path, split at the Policy gap

Date: 2026-07-12
Status: **accepted**
Accepted: 2026-07-12 — executive (general, claude), after three rounds of cross-agent adversarial review (Codex, read-only). Rounds 1 and 2 rejected the two predecessor proposals; round 3 returned ACCEPT-WITH-AMENDMENTS on this one, and all three amendments are incorporated above (Layer 4 publication guard; pre-registration pages may publish no results; `memory-systems-v1` is `incomplete`, not `concluded`).
Author: executive (general), 2026-07-12
Supersedes: ADR-0041 (rejected), which superseded ADR-0040 (rejected)
References: ADR-0038 (programmes as discovery plane), ADR-0029 (L2 extraction deferred), ADR-0027 (synaplex is the system), S1-P3 (two write paths to one store)
Review artifact: `supervisor/.reviews/adr-0040-codex-2026-07-12T03-30Z.md`

> **ACCEPTED. Authorizes Phase 1 only** — the `Claim`, `Evidence`, and `EventLogEntry`
> emitters, under the acceptance criteria below. It authorizes **no** `Decision` emitter,
> **no** `Policy` emitter, **no** runner, **no** rival Claim, and **nothing** resembling the
> reverted `lab/campaign` kernel. A later session citing this ADR as blanket permission for
> an emission-adjacent build is misreading it.

## Context

Two proposals for a synaplex canon emission path have now been rejected under
cross-agent adversarial review. Both rejections were productive and neither is
re-litigated here; the review artifact holds the full trail. What matters is what the
two rounds established, because it determines the shape of this one.

**Round 1 (ADR-0040 rejected).** Its scope — Claim, Evidence, Decision, EventLogEntry,
explicitly *not* Policy — cannot run an eval end to end. `decision.schema.json` requires
`policies_in_force` with `minItems: 1`; `canon.md` validator rule 5 requires the cited
Policy to exist. No Policy, no Decision, no eval conclusion.

**Round 2 (ADR-0041 rejected).** Adding Policy exposed something worse. `policy.md`
§Classes offers exactly two mutability classes:

- **`operational`** — "Agent-mutable within constitutional ceilings," amendable by a
  `Decision(kind=amend_policy)` citing Evidence.
- **`constitutional`** — "Permanently outside agent authority," principal-only, and
  framework-level by every example given (capital ceilings, kill-switch, amendment
  authority itself).

A pre-registered eval promotion gate is **neither**. Operational means an agent can move
the gate after seeing Evidence — the exact post-hoc flexibility pre-registration exists to
close. Constitutional means every eval threshold becomes principal-amendable-only canon,
inflating the constitutional surface until it means nothing. ADR-0041 tried to close the
hole with prose constraints on `amendment_authority`; `policy.schema.json` types that field
as a bare array of principals, so the constraint is not merely unenforced, it is
**unwritable**.

### The actual gap

> **Canon v0.1.0 cannot express a frozen, pre-registered, eval-local promotion gate.**

Not `minItems: 1` — that is canon working as designed (obligation 7: "What policy applied at
the time of each Decision?" A Decision governed by no policy is unanswerable). The gap is the
mutability model. And project `CLAUDE.md` is unambiguous about what happens next: *"If a lab
eval exposes a canon gap, escalate via context-repository adversarial review to bump the spec,
not a local workaround."* ADR-0041 cited that rule and then broke it. This ADR obeys it.

### The way through

The gap does not block the emission path. It blocks **one envelope type**.

| Envelope | Requires a Policy? |
|---|---|
| `Claim` | no |
| `Evidence` | no |
| `EventLogEntry` | no |
| `Decision` | **yes** — `policies_in_force`, `minItems: 1` |

Verified against all four schemas' `required` arrays. `Decision` is the *only* envelope with
a Policy dependency, and it is the *last* thing an eval emits. So the path splits cleanly,
and the split falls exactly where the gap is.

## Decision

Build the emission path in two phases, divided at the Policy gap. **Phase 1 is authorized by
this ADR. Phase 2 is not.**

### Phase 1 — authorized now

Emitters for **`Claim`, `Evidence`, `EventLogEntry`**. No Policy dependency, no workaround,
and every one has a real near-term consumer:

- `EventLogEntry(phase_transition)` + `EventLogEntry(methodology_log)` — required by
  `canon.md` §Phase invariants on probe entry. Nothing can enter probe without them.
- `Claim` — the control-arm rival Claim (separately authorized; see Sequencing).
- `Evidence` — everything a run produces.
- `EventLogEntry(canon_violation)` — refused writes are recorded, not dropped.

This is the whole of what the lab needs to **enter probe and produce Evidence**.

### Phase 2 — NOT authorized; blocked on a named canon gap

Emitters for **`Decision` and `Policy`**. Blocked until context-repository resolves how canon
expresses a frozen eval-local gate. Not blocked on indecision, not blocked on a missing
session — blocked on a spec question with an owner and an escalation, filed with this ADR.

**Consequence, stated plainly:** `memory-systems-v1` will be able to enter probe and generate
Evidence, and will **not** be able to conclude, until Phase 2 lands. That is an honest partial
unblock and it is better than both alternatives — building the Decision emitter on a Policy we
cannot construct honestly, or leaving the lab unable to write at all for a fourth month.

**`memory-systems-v1` is `incomplete`, not `concluded`.** It stays that way until a
validator-passing Decision exists. No surface — front door, writeup, status file, or public page —
may describe it otherwise.

### The publication guard (the hazard the split creates)

A store holding Claims and Evidence with **zero Decisions** is a loaded gun pointed at Layer 4.
Project `CLAUDE.md` gates publication on *"the matching canon envelope passing validation"* — and a
valid **Evidence** envelope satisfies that reading. Nothing today stops a future session from
emitting Evidence, seeing `recall@1 = 0.62`, and shipping "Letta scores 0.62" as a finding with no
Decision behind it.

That is not a hypothetical. A public page already exists at
`site/src/pages/lab/memory-systems-v1.astro`; it says results *"will be appended here."* And the
Claim's own second falsification criterion pre-registers that the held-out suite may **reverse the
ordering**, and that *"the Decision MUST note this as an override."* Publishing Evidence before the
Decision would publish precisely the finding the Decision exists to override.

So the split imports an obligation. **Layer 4 must refuse to publish any eval result, finding,
conclusion, or promotion unless it is backed by a validator-passing `Decision` carrying
`policies_in_force`, `chosen_claim_id`, and cited `Evidence` covering every published claim.**

A pre-registration page may remain public **only while it publishes no results, findings, or
conclusions.** The existing page qualifies today and must not be "updated with early numbers" while
Phase 2 is blocked. Until Phase 2 lands, no Decision can exist — so under this guard, **no results
page can ship at all.** That is the correct behavior, and it is fail-closed by construction: the
guard needs no judgment call, because the object it requires cannot yet be built.

### Escalation (filed with this ADR, not deferred)

A handoff to context-repository stating the gap: canon needs a way to express a promotion gate
that is frozen at pre-registration, agent-immutable for the life of the eval, and *not*
framework-constitutional. Candidate shapes are named there as input, not mandate —
context-repository owns canon. Note for whoever picks it up: if the answer involves a
constitutional Policy, its `issuer` and `amendment_authority` are a principal question, since
an agent minting a constitutional Policy and naming itself its amendment authority is
self-authorization by construction.

## Carried forward from the rejected proposals (each survived both reviews)

### The id contract

Pin **`sha256(statement.lower())[:16]`** in one module, with a test asserting
`b7ff216f4eec6e58` reproduces. This is the S1-P3 obligation: the first programmatic writer to
a store reconciles with what is already there.

Record the verified fact that **atlas's stricter derivation reproduces the same id** —
atlas's `claim_hash()` = `sha256(claim_canonical(statement))[:16]` (strip → lower → collapse
whitespace → strip trailing punctuation) returns `b7ff216f4eec6e58` on this Claim's statement.
ADR-0040 asserted the two instances use *different* id contracts and proposed to document the
divergence; that was false. Same hash family, same truncation, same lowercase — atlas's is a
strict refinement in normalization.

Do **not** vendor atlas's helper. Copying a repo-local utility across a repo boundary with no
shared test surface creates a second copy of a contract that can drift silently — the exact
class S1-P3 names — and L2 `discovery-runtime` extraction stays deferred per ADR-0029 until
synaplex has run several evals.

Two consequences to hold:

- The contract is **case-insensitive**: two Claims differing only in case collide. Made safe
  by **refusing to write on collision**, loudly — not by changing the hash. A refusal is
  recoverable; a silent overwrite of a pre-registration is not.
- Evidence and EventLogEntry ids **do** genuinely diverge from atlas (which uses domain-native
  ids, and 12-char evidence ids against 16-char claim ids). Nobody may later write a
  cross-instance join assuming a shared scheme.

### The anti-kernel guard is behavioral — and its limits are admitted

> **The emitter serializes, validates, and writes. It never selects what to emit.**

No code in the emission path may compute *which* Claim to register, *which* Decision to reach,
or *when* to emit. Inputs come from the caller; the emitter's only decisions are *"is this
valid"* and *"does this already exist."* The distance from "emit a Decision" to "compute which
Decision to emit" is short and downhill, and it is the slope `15edd38` slid down.

ADR-0040 guarded this with "no file under `lab/campaign/` exists" — a *path* check that the
same kernel rebuilt at `lab/pressure/` would satisfy. This is stronger, but review is right
that it is **not a proof**: any mechanical form of it is a structural grep/AST check that
misses synonyms, dynamic dispatch, and config-driven selection. It is a tripwire plus review
discipline, and it is recorded as such. A guard whose limits are documented is worth more than
one whose limits are discovered.

### ADR-0038 alignment — three guarantees, honestly counted

Mechanically enforced:

1. **The emitter has no knowledge of Programmes.** It takes no Programme path, reads no
   Programme file, cannot be invoked "by" a Programme.
2. **Write-side path refusal.** Refuse any envelope whose `ArtifactPointer.uri`, `sources[*]`,
   or any other field points into `reasoning/programmes/`. This is new capability:
   `check_programmes.py` catches path citation at *scan* time, after the bad envelope is
   already in an append-only store. Refusing at write time makes it impossible rather than
   detectable.
3. **No provenance slot.** Per ADR-0038 §4, that a Programme led to a Claim lives in the
   Programme's graduation ledger, never in the Claim envelope.

**Not** mechanically enforced, and not advertised as such: content laundering. ADR-0038
§Reference direction says it in terms — *"The grep/path guard can catch path citation
laundering. It cannot catch copied content."* An emitter that hash-pins an artifact will pin
Programme prose copied into that artifact with no `reasoning/programmes/` path anywhere.
ADR-0040 claimed all four constraints were mechanical. Three are. The fourth is a
reflection-review obligation, and saying so is the difference between a guard and a
reassurance.

### The methodology id-drift: documented, not repaired, not reconciled in canon

`methodology.md` cites Claim `memory-systems-v1-h1` at two paths that do not exist; the real id
is `b7ff216f4eec6e58`. **This is not a canon violation.** Validator rule 7 requires
`ArtifactPointer.content_hash` to reproduce from the artifact — it does (`sha256:45916c9f…`,
re-verified). The stale label is prose *inside* the artifact, not a canon reference. Canon is
self-consistent.

Do not repair the artifact — it is hash-bound, and repairing it destroys the pre-registration it
documents. Do not manufacture a reconciliation envelope either: an earlier draft proposed
recording the mapping in `EventLogEntry(methodology_log).summary`, and review killed it, rightly
— `summary` is free-form narrative, and audit content placed there makes audit depend on prose
parsing. The drift is recorded in `CURRENT_STATE.md` and project `CLAUDE.md`, where readers
actually look. It stays there.

## Out of scope — explicitly

- **`Decision` and `Policy` emitters.** Phase 2. Blocked on the canon gap.
- **No revival of `lab/campaign`.** No Campaign object, scheduler, outcome map, publish gate, or
  manifest. ADR-0038 §Cleanup governs; a downstream pressure kernel is a separate decision with
  its own safety requirements. Neither this ADR nor its rejected predecessors are a step toward
  one.
- **No canon schema bump, and no local workaround for one.** L1 stays frozen at v0.1.0. The gap
  goes to context-repository.
- **No automation.** Nothing in intake, reasoning, or the reflection loop may invoke the emitter.
  Emission is session-initiated and reviewed. An emitter on a timer is a machine for
  manufacturing canon.
- **No runner.** Executing `memory-systems-v1` is separate engineering under separate
  authorization.
- **No rival Claim.** The control-arm remedy is a *use* of this path, not a grant of it.

## Sequencing

1. **Now:** Phase 1 emitters (Claim, Evidence, EventLogEntry).
2. **Then:** cross-agent adversarial review before merge — synaplex is a Claude session, so
   route to Codex. Required by project `CLAUDE.md` for canon-adjacent changes.
3. **In parallel:** context-repository resolves the canon gap. Phase 2 unblocks when it does.
4. **Then, separately authorized:** the control-arm rival Claim (handoff
   `synaplex-memory-systems-v1-missing-control-arm-2026-07-12T02-05Z`). Its pre-registration
   window is open only while zero Evidence exists — but with no runner, nothing is closing it
   imminently. It goes through the reviewed path; it is not rushed ahead of one. Hand-authoring
   it is what produced the drift being cleaned up here.
5. **Then, separately authorized:** the runner.

The emitter is **necessary but not sufficient**. ADR-0040 framed it as *the* blocker; the runner
does not exist either (0 python files under `lab/`), and now the Decision emitter is gated too.
`memory-systems-v1` has three blockers and this ADR clears one. Naming one blocker as "the"
blocker is the overclaim that let this sit for 12 weeks.

## Acceptance criteria

1. Id-contract module with a test asserting `b7ff216f4eec6e58` reproduces under
   `sha256(statement.lower())[:16]`.
2. Emission-time validation per `canon.md` §Validator-level rules, refusing the write on
   violation. In scope for Phase 1: **rule 1** (`role_declared_at ≤ emitted_at`) and **rule 7**
   (`ArtifactPointer.content_hash` reproduces from the artifact at `uri`). Rules 2–6 and 8 govern
   Decision/Policy fields Phase 1 does not emit — the validator must **refuse** if those fields
   appear, not silently pass them.
3. Append-only enforcement, with a test proving an overwrite attempt raises **and leaves the
   envelope on disk byte-unmodified**.
4. Id-collision refusal, with a test: two statements differing only in case must produce a loud
   refusal, never an overwrite.
5. Write-side Programme-path refusal, with a test — and a docstring stating plainly that it does
   **not** cover copied content.
6. `EventLogEntry(canon_violation)` emitted on every refused write.
7. A structural check that the emitter does not select what to emit: no scheduler, no outcome
   map, no rival generation, no code computing which Decision to reach — anywhere in the repo,
   not merely under `lab/campaign/`. Its limits (grep/AST heuristics; misses synonyms and dynamic
   dispatch) are documented in the check itself, not discovered later.
8. Any "identical" assertion anywhere in the emitter is **canonical-JSON equality, not byte
   identity** — the Claim's thresholds contain the lexeme `0.80`, which round-trips to `0.8`
   through any normal serializer. A byte-identity test would be born broken.
9. **The Layer 4 publication guard, enforced in `python -m integrity` and fail-closed:** no
    reader-facing surface may publish an eval result, finding, conclusion, or promotion for a Claim
    unless a validator-passing `Decision` exists citing that Claim and the Evidence behind it. A
    pre-registration page that publishes no results is permitted. Since Phase 2 is blocked, no
    Decision can exist, so this guard currently forbids every results page — which is the intended
    behavior, not a limitation of it.
10. `python -m integrity` and `reasoning/check_programmes.py` still clean.
11. Cross-agent adversarial review before merge (route to Codex).
12. No file under `lab/campaign/`, and no equivalent kernel under any other path.
13. No `Decision` or `Policy` emitter exists. If implementation finds itself needing one, that is
    the canon gap biting — stop and escalate, do not construct a Policy.

## Consequences

- The lab gains the ability to write canon. This is the highest-consequence change available in
  this repo: an emitter is what makes an append-only, hash-pinned store *writable*, and therefore
  corruptible. The scrutiny it deserves is not proportional to the amount of code.
- `memory-systems-v1` can enter probe and produce Evidence. It **cannot conclude** until the
  canon gap resolves. One of three blockers cleared, and the other two are named with owners.
- **No workaround is taken.** The gap is escalated on the surface that owns it. This is the
  outcome the project's own rule demanded and that two prior proposals talked themselves out of.
- The status vocabulary in `supervisor/CLAUDE.md` §Decisions
  (`proposed | accepted | superseded-by-NNNN`) has no way to record a rejected proposal — two now
  exist. Accepting this ADR authorizes amending it to
  `proposed | accepted | rejected | superseded-by-NNNN`. A governance surface that can only record
  approvals is not a governance surface.

## Alternatives considered

- **Accept ADR-0041 with its Policy resolution.** Rejected. It mandates governance semantics canon
  cannot express (`amendment_authority` is a bare array of principals) and would have minted an
  `operational` Policy — a gate an agent can move after seeing Evidence — to protect a
  pre-registration. It is the local workaround the project's own rule forbids.
- **Escalate and build nothing until canon resolves.** Rejected. The Policy gap blocks exactly one
  envelope type. Blocking Claim, Evidence, and EventLogEntry on it would hold the lab hostage to a
  spec question they do not depend on, and would extend a 12-week parked state for no gain.
- **Make the eval's gate `constitutional`.** Rejected. It is principal-only and framework-level by
  every example in `policy.md`. Every eval threshold in every future eval would become
  constitutional canon, which inflates the constitutional surface until the class means nothing.
- **Emit a `Decision` citing atlas's existing Policy.** Rejected. It lives in `atlas/.canon/` under
  `instance_id: atlas`. Citing it cross-instance is precisely the cross-instance join hazard this
  ADR warns against two sections up.
- **Do nothing.** Still a real option, still costed honestly: the lab cannot write,
  `memory-systems-v1` stays parked, and the "publication + evaluation lab" half of ADR-0027 stays
  aspirational. A deliberate pause is fine. A pause by omission is what produced the last 12 weeks.
