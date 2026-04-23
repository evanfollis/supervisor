# ADR-0029: The synaplex loop — five-layer operational pipeline

Date: 2026-04-23
Status: accepted
Accepted: 2026-04-23
Author: executive, workspace-root session 2026-04-23
Review: supervisor/.reviews/adr-0029-synaplex-loop-2026-04-23T17-27Z.md (Codex gpt-5.4, reasoning=high; 3 findings; all addressed in §Adversarial review response below)
References: ADR-0027 (synaplex is the system), ADR-0026 (superseded by ADR-0027), ADR-0013 (self-reflection first class), ADR-0020 (action-default contract)

## Context

ADR-0027 established the conceptual shape of synaplex.ai: the system itself,
with canon + knowledge system + lab + publication + command as load-bearing
layers, pods (atlas, skillfoundry) as bidirectional exploratory probes, and
the strange-loop structure as architectural rather than decorative.

What ADR-0027 does *not* specify is how the system actually runs — the
operational pipeline by which external signal enters, becomes validated
knowledge, gets published, and produces friction that refines the system
itself.

The workspace has, to this point, operated with near-zero external intake:
no RSS ingestion, no arxiv scanning, no podcast transcription, no per-beat
scoring, no daily or weekly synthesis of the external landscape. Atlas's
signal detectors read OHLCV data; they do not read academic literature.
Skillfoundry has no market-intelligence or competitive-landscape intake.
The closed loop this produced — the system diagnosing its own state
against its own prior diagnoses — is the mechanical cause of the 2026-04-21
through 2026-04-23 "80h perfect-diagnosis-zero-execution" window: the
reflection layer had no new external evidence to pressure-test its own
conclusions against.

Separately, on 2026-04-23, the principal directed that execution cadence
should be concurrent-agentic rather than attended-serial ("multiple forward
moving sessions per day, run concurrently"). The existing tick + reflection
+ synthesis infrastructure provides the substrate for this; what has been
missing is a continuous operational pipeline that fans work out across the
pods rather than serializing through attended sessions.

This ADR names that pipeline as the **synaplex loop** and establishes its
five layers, their contracts, and the invariants they must uphold. It is
downstream of ADR-0027 and operationalizes it.

## Decision

**The synaplex loop is one circulatory system, five phases:**

### Layer 1 — Intake

External signal ingestion. Adapters per source:
- RSS/Atom (blogs, newsletters, vendor announcements)
- arxiv OAI-PMH (cs.AI, cs.CL, cs.LG, q-fin)
- HackerNews Firebase API (top, new, Show HN, Ask HN)
- Reddit JSON API (r/LocalLLaMA, r/MachineLearning, r/algotrading — agent-operated, not principal-authenticated)
- GitHub trending API (AI/agents/quant orgs)
- Substack (Latent Space, Import AI, The Batch, Quantocracy, Not Boring, Delphi, Glassnode Insights, others)
- Podcasts via RSS + Whisper transcription (Latent Space, MLST, Cognitive Revolution, No Priors, Excess Returns, Flirting with Models, Acquired, Invest Like the Best, others)

Raw items land at `runtime/intake/raw/<source>-<date>.jsonl`, content-hashed and deduplicated. Items are scored per-beat by a Sonnet classifier and land at `runtime/intake/scored/<beat>/`. Daily digests per beat at `runtime/intake/digests/<beat>-<date>.md`; weekly synthesis per beat at `runtime/intake/synthesis/<beat>-<iso-week>.md`.

**Three beats** match three pods:
- `agent-platforms` → synaplex editorial + lab surface
- `systematic-trading` → atlas
- `venture-discovery` → skillfoundry

Intake is cron-agentic. No attended sessions required.

### Layer 2 — Reasoning

Daily per-beat job: load current per-pod canon state + most recent intake synthesis → run conjecture/criticism. For each beat, the reasoning layer asks:
- What claims does this week's evidence support or undermine in existing canon?
- Where does new evidence pressure-test existing canon claims?
- What hypotheses should atlas consider generating, what probes should skillfoundry consider running, what lab evaluations become newly relevant?

Outputs are **candidate** Claim / Evidence / Decision envelopes written to the relevant pod's `.canon/` in a `candidates/` subdirectory — not yet promoted. Must honor ADR-0026 canon schema (preserved by ADR-0027) and pre-registration immutability. The reasoning layer proposes; validation and pod-local logic dispose.

### Layer 3 — Validation (woven, not terminal)

Validation is not a gate at the end of the pipeline. It is woven throughout:
- **Intake layer**: content-hash dedup, source-authenticity checks, scoring rationale stored and auditable
- **Reasoning layer**: every candidate envelope carries a provenance chain back to the intake items it used
- **Validation layer proper**: (a) automatic adversarial review (Codex via `supervisor/scripts/lib/adversarial-review.sh`) on every promoted claim; (b) counter-search — for each candidate, query the intake corpus for strongest disagreement and attach as Evidence if found; (c) canon integrity (hash, referential integrity, schema) nightly
- **Presentation layer**: every published writeup references the canon envelope hash it derives from; post-hoc edits produce new envelopes, not silent overwrites

The layer-proper is the sharpest pressure: every promoted claim faces an adversarial review and a counter-search. The weaving means that by the time a claim reaches the layer-proper, it has already survived several lower-amplitude validations.

### Layer 4 — Presentation

Accepted claims → agent-drafted MDX writeups into `projects/synaplex/site/src/content/editorial/` or `.../lab/`. Weekly newsletter composed from the week's accepted claims → Buttondown draft. Drafts are always agent-ready; principal approve-to-publish gate for brand-facing output. Canon envelope is primary; writeup is derivative and must reference the envelope hash.

Publication is **topology, not timeline** per ADR-0027: each new piece builds and refines the latent structure; old pieces do not age out but become foundations for newer ones. Information architecture reflects conceptual topology, not publish-date.

### Layer 5 — Friction + self-reflection (cross-cutting, not downstream)

Every layer emits typed success/failure events to `runtime/friction/events.jsonl`. Minimum event shape:
```json
{"ts":"<iso>","layer":"intake|reasoning|validation|presentation","source":"<adapter or subcomponent>","eventType":"<success|failure|stuck|escalated>","reason":"<one-line>","ref":"<path or id>"}
```

An auto-classifier runs on the friction log and promotes recurring failure classes to FR candidates in `supervisor/friction/`. Classes above threshold become formal FRs and enter the existing synthesis loop. The synthesis job is extended to consume friction events alongside reflections, so the existing carry-forward escalation rule applies across the full stack, not just tick skips.

**Infrastructure friction (adapter broke on malformed arxiv XML) and research friction (claim X could not be validated because upstream data source is missing) are the same kind of thing.** They are captured the same way, promoted by the same process, and refined through the same policy loop. This collapses a distinction that would otherwise require two parallel friction systems.

**The friction layer is itself in the loop.** It emits events about its own operation. It can be superseded. The classifier's policy is itself revisable by synthesis. This is the essence (ESSENCE.md) operationalized at the pipeline level: the methodology applied to itself.

### Invariants

1. **Every layer emits typed events.** Intake, reasoning, validation, presentation, and friction each emit structured events for success, failure, stuck, and escalation states. A silent layer is indistinguishable from a stuck one (S3-P2 principle, generalized).

2. **Canon envelope is primary; derived surfaces reference envelope hash.** A published writeup, a newsletter paragraph, a reader-facing claim must all resolve to a specific envelope hash. Post-hoc changes produce new envelopes.

3. **Validation is woven, not terminal.** No layer may treat validation as "the step that happens at the end." Each layer's outputs must be auditable by later layers.

4. **Friction capture is universal.** Infrastructure failure and research failure are the same kind of thing. No separate systems.

5. **The synaplex loop is itself in the conjecture/criticism loop.** This ADR is provisional. When synthesis finds a better shape, the loop is superseded.

## Workspace CLAUDE.md amendments authorized by this ADR

This ADR authorizes the following amendments to `/opt/workspace/CLAUDE.md`
(already applied in-session 2026-04-23):

- **INBOX saturation exception.** When INBOX holds >5 unconsumed items sharing the same root cause, synthesis may suppress additional URGENT writes for that root cause and record the suppression in the synthesis file itself. Reason: adding noise to an unread queue is not escalation; the tick's S3-P2 writer also dedupes URGENTs by reason-hash (supervisor-tick.sh FR-0043 patch; commit 79fae2f).
- **Dispatch obligation.** When a synthesis proposal lands in `runtime/.meta/cross-cutting-*.md`, the executive must dispatch a delegated project session within 24h via `runtime/.handoff/<project>-*.md` handoff, or record an explicit deferral reason in `supervisor/decisions/` or `runtime/.meta/`. Synthesis proposals sitting >24h without dispatched action or recorded deferral escalate as FR-class structural issues. Reason: the reflection/synthesis loop is a work queue, not a diagnostic archive; treating proposals as read-and-file produces the "80h perfect-diagnosis-zero-execution" failure class.

These amendments codify the executive-to-project dispatch pattern the synaplex loop depends on. Without the dispatch obligation, synthesis proposals for the loop itself will sit unexecuted exactly as they did for the 3 cycles preceding this ADR.

## Consequences

### Directory structure

- `projects/synaplex/intake/` — Layer 1 adapters + scoring + digest/synthesis code. Systemd timers.
- `projects/synaplex/reasoning/` — Layer 2 per-beat daily jobs.
- `projects/synaplex/validation/` — Layer 3 counter-search + integrity jobs. (Adversarial review continues to route through `supervisor/scripts/lib/adversarial-review.sh`.)
- `projects/synaplex/site/src/content/` — Layer 4 editorial + lab MDX.
- `runtime/intake/raw/`, `runtime/intake/scored/`, `runtime/intake/digests/`, `runtime/intake/synthesis/` — Layer 1 data
- `runtime/friction/events.jsonl` — Layer 5 event log; consumed by synthesis.
- `supervisor/friction/` — existing FR directory, now receives auto-promoted candidates from the friction classifier.

### Dispatch pattern

The executive writes handoffs to project sessions via `runtime/.handoff/<project>-*.md` for each layer's build and maintenance. Executive does not implement project code directly (charter: `/opt/workspace/supervisor/AGENT.md`). The synaplex project session owns layers 1–5 implementation; atlas and skillfoundry sessions consume candidate envelopes from Layer 2.

### Cost envelope

- RSS/arxiv/HN/Reddit/GitHub ingestion: free.
- Podcast transcription via Groq `whisper-large-v3`: ~$0.10/hour × ~20hr/week ≈ $2/week.
- Claude Sonnet scoring at ~2k items/day × ~500 tokens ≈ $3/day.
- Claude Sonnet reasoning passes per beat per day: ~$5/day.
- Total: ~$100–200/month for research-grade intake + reasoning.

### Integration with existing infra

- Existing 12h reflection cadence (`workspace-reflect.timer`) consumes friction events in addition to git log + telemetry + prior reflections.
- Existing synthesis cadence (`workspace-synthesize.timer`) applies carry-forward escalation rules to friction-promoted FRs identically to reflection-promoted ones.
- Existing supervisor tick continues to be the lowest-level substrate heartbeat; the synaplex loop is higher-amplitude operational cadence.
- Existing canon adapters (atlas, skillfoundry-valuation) continue to emit envelopes; Layer 2 adds candidate envelopes to the same stores.

### Supersession

This ADR does not supersede ADR-0026 or ADR-0027. ADR-0026 was superseded by ADR-0027 (name + framing). This ADR operationalizes ADR-0027's conceptual framing.

## Open design questions (not resolved by this ADR)

1. **Friction event schema vs canon ArtifactPointer compatibility.** Friction events are append-only JSONL. Should they also be promotable to canon Evidence when they represent load-bearing findings? Resolution: defer until first 4 weeks of friction events accumulate and a natural pattern emerges.

2. **Layer 2 reasoning promotion threshold.** How much external evidence, of what quality, is required to promote a candidate claim to a full Claim envelope? Deferred to first Layer 2 implementation pass + adversarial review of the proposed thresholds.

3. **Podcast transcription priority vs text-first ingestion.** Podcasts are the highest-leverage source (no one else indexes them for structured retrieval) but also the most expensive and slowest. First-pass: text-first ingestion (RSS + arxiv + HN + Reddit + GitHub + Substack) running in production before podcast pipeline ships.

4. **Counter-search vs adversarial review overlap.** Counter-search finds strongest disagreement in the intake corpus; adversarial review routes to Codex for structured critique. These may be complementary (counter-search is fast and source-grounded; adversarial review is deeper but slower) or redundant. First 8 weeks of operation should clarify.

5. **Layer 4 principal approval mechanism.** Drafts are always agent-ready; principal approve-to-publish gate for brand-facing output. Shape of approval surface not specified — inbox? cli flag? front-door markdown checklist? Deferred to first draft pipeline reaching the gate.

## Alternatives considered

- **Bolt intake onto existing reflection job.** Rejected: reflection is per-project diagnostic; intake is cross-project signal ingestion. Conflating them produces a single job that can't be scaled per-source or paused per-pod.
- **Synthesis as the reasoning layer.** Rejected: synthesis operates over reflection output; it does not load external evidence. Naming intake→reasoning as a separate pair keeps the pipeline shape legible and avoids overloading synthesis semantics.
- **Human-reviewed weekly digest only, skip reasoning layer.** Rejected: the failure class this ADR addresses is precisely the absence of automated reasoning on external evidence. Humans cannot read arxiv daily at scale; if the system can't convert signal into canon pressure without a human bottleneck, it reproduces the attended-serial execution problem.
- **Friction capture as two separate systems (infra vs research).** Rejected: see Decision §Layer 5. One system that captures both is simpler, cheaper to maintain, and enables cross-class pattern detection the synthesis job can surface (e.g. "infra failure correlates with research stagnation in this beat").

## Adversarial review

This ADR is consequential — it specifies the operational pipeline for the
system ADR-0027 defines. Warrants Codex adversarial review via
`supervisor/scripts/lib/adversarial-review.sh` before status transitions
from `proposed` to `accepted`.

Target artifact: `.reviews/adr-0029-<iso>.md`.

Review scope: pressure-test (a) the five-layer decomposition (is the boundary between reasoning and validation load-bearing or arbitrary?); (b) the woven-validation claim (is this actually different from "validate at each step" or just rebranding?); (c) the friction-unification claim (do research and infra frictions actually share enough structure to be captured the same way?); (d) the cost envelope (are the per-beat reasoning costs realistic at scale?); (e) the dispatch obligation (does 24h create enough pressure without crowding out thoughtful deferral?); (f) whether this ADR's amendments to `/opt/workspace/CLAUDE.md` should have preceded this ADR or correctly follow it.

## Adversarial review response (2026-04-23T17:27Z)

Review artifact: `supervisor/.reviews/adr-0029-synaplex-loop-2026-04-23T17-27Z.md` (Codex gpt-5.4, reasoning=high, 91.4k tokens, read-only sandbox).

Three findings, each addressed with a concrete operational control that becomes a required feature of the Layer 1/2 build rather than an open question:

### Response to Finding 1 — "hallucination amplifier" risk from intake→reasoning producing low-quality candidates at scale

**Operational controls:**

- **Per-source trust tracking.** Each intake source accumulates a 14-day rolling `promotion_rate` (ratio of that source's scored items that produced an eventually-promoted Claim). Sources with <5% promotion rate over a rolling window enter a reduced-weight state; <2% triggers auto-pause and friction-escalation for principal review.
- **Scoring-accuracy tracking.** If a per-beat Sonnet scorer's items fail downstream validation (Layer 3) at >30% over 7 days, the scorer config is auto-paused and the failure emits an FR candidate. The scoring prompt is treated as a reviewable artifact in `projects/synaplex/reasoning/` (under version control), not a runtime-tunable opaque config.
- **Reasoning-layer sanity floor.** Layer 2 MUST emit a brief justification per candidate envelope (≤2 sentences in the envelope's `reasoning_note` field) tying it to at least one specific intake item. Candidates without justifications are rejected at write-time. This prevents "Sonnet generated a plausible-sounding claim with no source grounding" — a known failure mode of LLM pipelines at scale.
- **Explicit low-volume bootstrap.** First 4 weeks of operation run at a throttled cap: max 5 candidates/beat/day into `.canon/candidates/`. The cap lifts only after the first full synthesis cycle demonstrates the validation layer is keeping up. This forces the failure mode to surface before it has scale to hide in.

### Response to Finding 2 — backlog poisoning / stale-candidate accumulation

**Operational controls:**

- **Candidate TTL.** Every candidate envelope carries `expires_at` = creation_time + 30 days. A nightly integrity job moves expired candidates to `.canon/candidates/expired/` with a retention log. Expired candidates are not loaded by any downstream layer.
- **Quarantine path.** Candidates that fail any validation step (Layer 3) are moved to `.canon/candidates/quarantine/` with a reason code, not silently dropped. The quarantine is inspectable but not consumed by default.
- **Ownership.** The nightly integrity job is owned by the synaplex project session and reports via `runtime/friction/events.jsonl`. If the integrity job fails or skips, that is itself a friction event that synthesis will surface on the 3rd occurrence.
- **Rate limits enforced at write-time.** Layer 1 raw-intake capped at 200 items/source/day; Layer 2 reasoning capped at the bootstrap level above, then 10 candidates/beat/day after the 4-week bootstrap. Rate-limit breaches produce friction events and throttle the offending layer.

### Response to Finding 3 — Reasoning/Validation boundary collapse

**Accepted with explicit boundary semantics:**

- **Layer 2 MAY perform lightweight validation** (schema, referential integrity, deduplication against existing canon, basic sanity). This is not a boundary violation; it is basic hygiene every layer is expected to do.
- **Layer 3 is the *canonical pressure surface* for claim promotion.** Adversarial review, counter-search, and integrity enforcement are its authoritative scope. Claims are not promoted to canon until they pass Layer 3.
- **The distinction is amplitude, not kind.** Layer 2 validates enough to avoid emitting obvious junk; Layer 3 applies the pressure that gates promotion. Both touch validation-shaped work; only Layer 3 makes the promotion decision.
- **Explicit supersession clause.** If the boundary fully erodes in practice (Layer 2 becomes a mini-Layer 3 in realized code), that is a signal to collapse them into a single layer in a future ADR, **not** to force the five-layer shape as a rule. The five-layer decomposition is a conjecture about legibility; its correctness is validated by its durability under real use, not its theoretical purity. ADR supersession is the correct response if the boundary proves unstable.

### Status transition rationale

The review verdict was "directionally strong but not yet safe to accept as-is" with the three findings as the specific gaps. Each finding is now addressed with a concrete operational control that becomes a required feature of the Layer 1/2 build (not an afterthought). The synaplex session's Layer 1/2 handoff is augmented to name these controls as acceptance criteria. Accepting this ADR with these responses in place is materially different from accepting the ADR the review critiqued.

If Layer 1/2 implementation surfaces that any of these controls is wrong-shaped or unimplementable as specified, the correct response is a follow-on ADR refining them — the ADR remains in the conjecture/criticism loop per Invariant 5.

## Provenance

Articulated 2026-04-23 across three conversation turns with the principal,
workspace-root session at `/opt/workspace`. Principal's naming of the five
layers and the two cross-cutting concerns (validation throughout, friction
capture everywhere) is preserved verbatim in `runtime/.meta/` session
context; synthesis by the executive.

session_id: [workspace-root executive session 2026-04-23]
