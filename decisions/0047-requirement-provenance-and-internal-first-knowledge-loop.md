# ADR-0047: Requirement provenance and an internal-first knowledge loop

Date: 2026-07-12
Status: accepted
Author: workspace executive
Supersedes: ADR-0044's named first-cycle target only; the physical-home and
projection decisions remain accepted
References: ADR-0020, ADR-0036, ADR-0043, ADR-0044, ADR-0046

## Context

The first full Synaplex knowledge-loop handoff promoted `memory-systems-v1`
from an old pre-registration into the dominant objective. It then treated
Letta, MemGPT, and mem0 as executable evaluation subjects and their missing API
keys as principal blockers.

That route was not authorized by the principal's intent. Letta was an
imperfect example of a broader context-repository idea, not a requested vendor
evaluation or platform dependency. The route also contradicted ADR-0036, which
already prohibits metered model APIs and requires Claude/Codex subscription-CLI
failover.

This was not only an execution mistake. The control plane was inadequate in
three explicit ways:

1. it had no effective provenance boundary between an illustrative example and
   an executable requirement;
2. a stale active issue and project front door were allowed to contradict an
   accepted cost/provider Decision for weeks; and
3. downstream agents could convert an unauthorized external dependency into a
   credential escalation instead of rejecting the malformed objective.

## Decision

### Requirement provenance

- External products, vendors, papers, and architectures mentioned as examples
  are `illustrative` by default.
- Promotion to `candidate` or `authorized` evaluation subject, dependency, or
  spend target requires an accepted Decision or explicit principal instruction.
- Every external dependency in an executive handoff must cite that authority
  and be checked against higher-authority provider, cost, privacy, and security
  Decisions before dispatch.
- The handoff dispatcher enforces the boundary for new project handoffs: it
  requires non-empty `authority`, `external_dependencies`, and
  `policy_compatibility` frontmatter. `external_dependencies` is the scalar
  enum `none` or `authorized`; authorized dependencies additionally name
  `dependency_authority` and `dependency_details`. The dispatcher quarantines
  malformed handoffs intact outside the PM direct-scan path, emits telemetry,
  and writes a deduplicated supervisor escalation.
- A missing credential for an unauthorized dependency is not a blocker. It is
  evidence of an invented requirement; the route must be removed or redesigned.
- Project PMs are required to reject contradictory handoffs rather than execute
  them silently.
- This mechanical gate proves declaration, not semantic truth. A dishonest or
  mistaken agent can still misstate authority. Cross-agent review and PM
  disagreement remain the semantic boundary; this limitation stays visible as
  active architectural pressure rather than being described as solved.

### Model execution

- No Letta, mem0, Anthropic, OpenAI, or other metered API key is authorized for
  this loop.
- Model-assisted work uses the existing Claude and Codex subscription CLIs.
  Capacity exhaustion routes to the other subscription provider. Execution
  hard-stops only when both subscription providers are capacity-blocked or the
  error is not capacity-related, exactly as ADR-0036 specifies.
- The existing usage and model-state telemetry requirement remains: retain full
  transcripts and append-only traces off the hot path, and record provider,
  model, role, status, latency, fallback source, and exposed or honestly
  estimated token counts. Telemetry failure must not block the knowledge loop.

### Vendor route disposition

- Preserve the generic canon emitter, frozen-gate, runner, and projection work
  where it is independently useful.
- Retire the Letta/mem0/vendor-comparison route canonically without emitting
  Evidence or implying a finding. Preserve its lineage as an abandoned
  conjecture, not an active objective.
- Do not emit a successor vendor Claim and do not mutate hash-bound historical
  records to hide the mistake.

### First full loop

The first complete loop is grounded in the platform's own empirical behavior.
The 2026-07-12 Command build/serve split-brain incident is the Programme signal,
not retroactive Evidence for a pre-registration.

The already-observed Command failure and its reproduction are retrospective
incident Evidence and a deterministic regression fixture. They are not a blind
experiment and must not be presented as novel discovery.

Before producing new Evidence, Synaplex must pre-register a genuinely
falsifiable transfer Claim: a named population of active workspace services, a
static risk predicate, and predictions made before inspecting each subject's
outcome. The candidate predicate is whether a long-lived process resolves
behavior-critical assets from a directory that a build/deploy job can mutate.
The methodology must say which services are in the population, how the predicate
is scored, and what observation would refute its predictive value.

An isolated mechanism fixture may pressure-test causality, but it must be
labeled as such and separate the variables with three arms:

1. served artifacts mutable, in-place build mutation;
2. versioned immutable artifacts, non-atomic activation; and
3. versioned immutable artifacts, atomic activation.

Pre-register the observation barriers/sampling schedule. Authenticated browser
hydration and behavior are the primary outcome; manifest/asset coherence is a
diagnostic, not an independent oracle. Liveness is recorded separately so a
green health endpoint cannot masquerade as behavioral correctness. Run only in
isolated fixtures or staging; do not deliberately impair a live service.

The resulting Decision must remain bounded to the evidence. The known Command
regression can support a Command-scoped invariant immediately; any cross-service
invariant depends on the prospective transfer Evidence. A likely candidate is:
a long-lived process must not serve behavior-critical build artifacts from a
directory that build jobs mutate, and activation must preserve artifact-set
coherence. It becomes reusable system knowledge only to the scope the new
Evidence supports.

The loop is complete only through ADR-0044's full chain: Programme, Claim,
Evidence, Decision, reconstructible invariant, public projection, concrete
consumption or reasoned refusal, and reflection with model-state provenance.

## Consequences

- The knowledge loop now studies the system through its own real failure and a
  newly controlled pressure test, rather than manufacturing a vendor campaign.
- ADR-0044's knowledge-system ownership and acceptance chain remain intact; only
  its prematurely selected first subject is superseded.
- The system's design failure is durable, inspectable knowledge rather than an
  implicit exception stepped over during implementation.
- Any future external comparison begins with explicit subject authority and a
  non-metered execution plan, or it does not begin.

## Alternatives considered

- **Keep the vendor evaluation but run it through subscription CLIs.** Rejected:
  this would fix billing while preserving the deeper intent error.
- **Rely on agent judgment without a dispatch contract.** Rejected: the same
  mistake had already survived multiple agents and contradicted an accepted ADR.
- **Treat the known Command fix as a new controlled discovery.** Rejected after
  adversarial review: it is a valuable regression fixture, but its known outcome
  cannot honestly support a novel transfer claim.

## Adversarial review

Reviewed with the opposing subscription model on 2026-07-12 before final
acceptance. The initial design was rejected. The accepted revision quarantines
malformed handoffs outside the PM scan path, rejects placeholder provenance,
keeps the semantic self-attestation limit explicit, updates the governed
synthesis-translator prompt, and replaces the confounded two-arm Command test
with a labeled regression fixture plus a prospective transfer claim and
three-arm mechanism design.
