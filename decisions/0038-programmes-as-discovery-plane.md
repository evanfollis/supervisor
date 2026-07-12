# ADR-0038: Programmes as the discovery plane for conjecture generation

Date: 2026-07-12
Status: accepted

## Context

The principal reviewed the Conjecture Laboratory white paper and identified a
real gap in the current platform: a single canon `Claim` is sturdy for audit,
but it is often too brittle as the unit of exploration. Good conjectures need
room for theory construction: external research, platform-detected patterns,
interdisciplinary analogies, mechanisms, implications, open tensions, and draft
claims before they are compressed into strict falsifiable canon objects.

The current system is strong at honesty: pre-registration, falsification,
contradiction handling, hash-bound artifacts, and decisions grounded in canon.
That strength must not be weakened. Any exploratory surface that can bypass,
soften, or launder itself into canon would damage the platform.

During discussion, an agent-initiated synaplex commit
`15edd38 Keep pre-registered lab claims under continuous pressure` added a
`lab/campaign/` runtime, rival claims, an outcome map, and a campaign manifest.
That work was not principal-authorized; it was a downstream effect of agent
handoff activity while the idea was still being discussed. It was reverted in
synaplex commit `ab6a1de` on 2026-07-12. This ADR records the agreed design so
future implementation does not infer authorization from that premature code.

Claude Fable 5 and Codex iterated on the design. The converged view:

- `Programme` is the upstream discovery-plane object.
- `Claim` remains the strict canon verification atom.
- Any downstream claim-pressure kernel, if rebuilt, is separate from
  `Programme` and must not be confused with it.

## Decision

Introduce **Programme** as the name for a durable, non-authoritative
discovery-plane workspace.

A Programme exists to improve conjecture quality by preserving the context that
generates good claims. It may hold conjectural material, but it has **zero
epistemic authority**. It cannot support, validate, decide, publish, or elevate
anything by itself.

### Plane contract

- **Programme**: discovery plane. Holds leads, signals, source pointers,
  mechanisms, analogies, platform patterns, open questions, tensions, draft
  claims, and a graduation ledger.
- **Claim**: verification atom. Lives in canon and carries falsification
  criteria.
- **Evidence**: canon-only, hash-bound, lineage-aware once canon supports that
  field.
- **Decision**: canon-only, with cited evidence, contradiction handling, policy,
  and exposure.
- **Writeup**: derivative presentation surface. It must derive from canon, not
  from Programmes.

### Authority contract

1. Programmes own conjectural state but have no epistemic authority.
2. Only canon Claims, Evidence, and Decisions can elevate anything.
3. A draft claim from a Programme graduates only through the normal canon
   emission path. Graduation carries no privilege.
4. Provenance that a Programme led to a Claim lives in the Programme's
   graduation ledger, not in the Claim envelope.
5. Canon envelopes, Decisions, Evidence, and public writeups must never cite
   Programme files as source authority.

### Reference direction

References are one-way:

- Programmes may point to canon object ids, intake content ids, friction event
  ids, and external URLs.
- Canon and published writeups may not point to Programme paths.
- Programmes must not copy or re-ingest external content into a parallel intake
  surface. They hold pointers and notes.

The grep/path guard can catch path citation laundering. It cannot catch copied
content. The copy/re-ingest ban is therefore a reflection-review obligation,
not a fully mechanical guarantee.

### Vocabulary contract

Programme-local structure must not use canon-reserved labels such as
`Evidence`, `Decision`, `Supported`, `Validated`, or
`contradictions_addressed`.

This ban applies to frontmatter keys, headings, table labels, and list labels.
It does not ban ordinary prose that discusses evidence in a paper, and it does
not ban clearly labeled references to real canon Evidence or Decision ids.

Allowed Programme-local nouns include: leads, signals, sources, tensions,
anomalies, mechanisms, draft claims, open questions, and graduation ledger.

When implemented, the banned structural vocabulary should be derived from canon
schemas rather than maintained as a second hand-copied list.

### Lifecycle and rent

Programme rent is measured by graduation verdict quality, not by draft volume.

A Programme is progressive when it produces draft claims that graduate into
canon and receive meaningful decisions. Falsified claims count as success when
they were useful, decidable conjectures. A Programme emitting many weak drafts
that never graduate is degenerating, not productive.

A Programme is degenerating when it repeatedly reframes without producing
decidable claims, emits many drafts that do not graduate, or preserves a theory
mainly by narrative patching.

Degenerated Programmes are archived, not deleted. Their ledger is negative
result memory about theory-shapes that failed to produce useful claims.

The existing reflection loop reviews Programme ledgers. No scheduler or scalar
rent score is authorized by this ADR.

### Location

The intended home is:

```text
projects/synaplex/reasoning/programmes/<slug>.md
```

This makes Programmes part of Layer 2's durable substrate. It does not build
Layer 2 automation. It gives later Layer 2 jobs somewhere honest to write.

Do not put upstream Programmes under `lab/`; lab is the Layer 3 authority and
evaluation surface. Co-location would imply authority the Programme plane does
not have.

### Downstream interface

The only authorized Programme interfaces are:

1. Graduate a draft claim through the normal canon Claim emission path.
2. Propose append-only verifier ideas to a downstream claim-pressure kernel,
   but only after such a kernel has been separately reviewed and authorized.

No other coupling is authorized by default.

## Cleanup

The premature synaplex campaign implementation was reverted:

```text
synaplex ab6a1de Revert "Keep pre-registered lab claims under continuous pressure"
```

If a downstream campaign/pressure kernel is rebuilt later, it must be reviewed
as project code and must not be treated as principal-approved because the
reverted commit existed.

Minimum safety requirements for any future downstream kernel:

- `alternative_claim_ids` and `outcome_map` are frozen at probe entry with a
  recorded canonical-serialization hash.
- The freeze is covered by an immutability test before evidence emission and
  before publication.
- `verifier_plan` and `validity_threats` are append-only after probe entry.
- A wrong frozen manifest is superseded under a new probe id, never edited in
  place.
- The kernel remains downstream of canon Claims and never becomes an upstream
  theory container.

## Consequences

- The platform gains a sturdy exploratory plane without weakening the strict
  canon layer.
- Conjecture quality can improve because claims no longer need to be emitted
  atomically from transient session thought.
- External research and platform observations can accumulate without becoming
  authority.
- The read-path laundering failure is explicitly named and guarded.
- Programme content can influence the platform only by producing claims that
  survive the existing strict path.

## Non-goals

- No UI.
- No graph database.
- No scheduler.
- No auto-ingest.
- No automatic Programme creation from intake.
- No Programme canon object.
- No softer truth labels.
- No claim elevation shortcut.
- No reuse of `Campaign` terminology for upstream Programmes.

## Alternatives considered

- **Use `Campaign` for the upstream object.** Rejected. The term was already
  used by agent-generated downstream pressure-kernel code, and it also risks
  confusing discovery-plane theory construction with verification-plane
  pressure.
- **Make Programme a canon object.** Rejected. Canon is the verification layer;
  Programmes deliberately have no authority.
- **Allow canon Claims to cite Programme provenance.** Rejected. This creates a
  citation slot through which conjectural narrative can be laundered into
  canon. Provenance lives in the Programme ledger instead.
- **Build runtime machinery now.** Rejected. The correct v0 is a markdown
  surface plus guards and reflection convention.

## Review

Claude Fable 5 and Codex converged on this contract on 2026-07-12 after
reviewing the Conjecture Laboratory white paper, synaplex/canon context, and
the premature `lab/campaign/` implementation. Claude's binding corrections
included:

- quarantine agent-initiated campaign code until reviewed;
- invert references so canon never cites Programme;
- freeze any downstream outcome map before evidence;
- derive banned vocabulary from canon schemas;
- name the grep guard's blind spot around copied content.

