# ADR-0043: Full-fidelity empirical records stay durable and off the hot path

Date: 2026-07-12
Status: accepted
Author: workspace executive, on direct principal instruction
References: ADR-0004, ADR-0012, ADR-0019, ADR-0030, ADR-0031, ADR-0039

## Context

The platform learns not only from object-level outcomes but from the complete
process that produced them: transcripts, model configuration, tool calls,
telemetry, reflections, syntheses, refusals, reversals, and supersessions. These
records are cheap to retain and impossible to reconstruct after deletion.

The existing implementation violated that intent in two ways:

- telemetry archives were deleted after 30 days;
- older reflection and synthesis artifacts were deleted to bound the working
  directory.

At the same time, keeping every record in the working set creates a different
failure: agents and scheduled jobs repeatedly scan history that is irrelevant
to the current decision. Preservation and operational salience are separate
concerns and need separate storage behavior.

The normalized session trace also omitted the model and reasoning state that
generated assistant messages, even though source transcripts expose those
fields. That prevents later analysis of whether observed behavior changed with
model family, model version, effort, context pressure, or service tier.

## Decision

Adopt a three-temperature empirical-record lifecycle.

### 1. Source records are retained at full fidelity

Raw Claude and Codex transcripts remain the canonical interaction record in
their native durable stores. Operational telemetry remains append-only JSONL.
Reflection and synthesis outputs remain preserved as generated artifacts.

No default age-based deletion applies to these records. An explicit future
retention limit requires a superseding ADR and must identify what information
becomes irrecoverable.

### 2. Hot indexes are bounded and rebuildable

Routine agents and jobs read bounded current surfaces:

- the active `events.jsonl` segment;
- the most recent reflections per project;
- recent syntheses and current-state files;
- normalized trace indexes rather than replaying every transcript.

These are access paths, not the sole copy of meaning. They may be regenerated,
compacted, or replaced without deleting their source records.

### 3. Cold history is compressed, not deleted

Rotated telemetry segments move under
`runtime/.telemetry/archive/events/`. Older reflection and synthesis artifacts
move under `runtime/.meta/archive/` as gzip files. Compression and archival are
maintenance work and are never prerequisites for the object-level knowledge
pipeline.

An archive failure emits operational pressure and preserves the uncompressed
source. It does not authorize data deletion and does not stop intake,
evaluation, canon emission, or publication.

### 4. Model-state provenance is part of the trace contract

When exposed by the source transcript, normalized assistant-message traces
record:

- provider and model identifier;
- reasoning effort;
- context and output token counts;
- service tier.

The configuration of the reflector itself must also be recoverable from its
execution telemetry or artifact metadata. Reflections may compare behavior
across model states, but must treat model state as a causal candidate, not a
causal conclusion.

### 5. Capture is observational, not authoritative

Transcripts contain what agents and users said; they do not prove that claimed
actions occurred. Reflection and knowledge promotion must triangulate transcript
claims against tool results, repository state, live services, and canon.

The empirical record supplies conjectures and audit evidence. It never bypasses
the normal Claim, Evidence, Decision, and policy path.

## Consequences

- The workspace retains the full historical substrate needed to study how its
  latent model and operating behavior change over time.
- The hot execution path remains bounded; growing history does not increase the
  normal scan set indefinitely.
- Storage use grows monotonically. Health capture must report archive size and
  growth rate so retention remains an explicit capacity decision.
- Native transcript formats remain provider-specific. The normalized trace is
  the cross-provider index, not an attempted replacement for those formats.
- Local retention increases the sensitivity of host backups. Access control and
  backup encryption are operational obligations, not reasons to discard the
  evidence.

## Alternatives considered

- **Delete old records after a fixed window.** Rejected: destroys unique
  empirical evidence and prevents longitudinal analysis.
- **Keep all records in active directories.** Rejected: preservation should not
  force every routine consumer to traverse the full history.
- **Store only normalized summaries.** Rejected: every normalization decision is
  lossy, and future questions cannot be predicted today.
- **Put transcripts into canon.** Rejected: raw interaction records are evidence
  sources, not automatically verified system knowledge.
