# ADR-0046: Public knowledge and private owner projections

Date: 2026-07-12
Status: accepted
Author: workspace executive, on direct principal instruction
References: ADR-0027, ADR-0029, ADR-0043, ADR-0044

## Context

Synaplex has two human-facing hostnames but their product boundary is stale.
The public site is a manually maintained Astro scaffold rather than a live
projection of the system's knowledge. Command was designed partly as a remote
terminal and session launcher; the principal can now launch Claude and Codex
directly from a phone, so that function no longer deserves to shape Command's
information architecture.

Building two independent dashboards would duplicate interpretation and let the
public and owner views disagree. Exposing runtime state directly through the
public site would couple availability to the operator host and create an
unbounded disclosure surface.

## Decision

Synaplex exposes one knowledge system through two projections.

### Public projection: `synaplex.ai`

The public site is the reader- and agent-addressable projection of accepted
system knowledge, research artifacts, lab work, and expert interpretation.

- Its source is a versioned, generated, public-safe projection under
  `projects/synaplex/knowledge/`, subordinate to validator-passing canon
  Decisions per ADR-0044.
- Static build output is preferred. Public availability does not depend on
  the hot operator runtime.
- Human pages and machine-readable records resolve to the same stable ids,
  provenance, validity, and supersession data.
- Programme material remains conjectural and cannot appear as evidence.
- Results require a valid Decision; insights are derivative and cite the
  knowledge and Evidence they interpret.
- Publication is default-deny for private fields: transcript bodies, local
  paths, raw telemetry, handoffs, secrets, owner-only decisions, and personal
  information do not enter the generated projection.

### Owner projection: `command.synaplex.ai`

Command is the authenticated owner dashboard and private operational projection
of the same system.

- It consumes the public-safe knowledge projection and adds private runtime
  overlays: loop health, freshness, blocked transitions, evaluation and model
  telemetry, pending Decisions, deployment state, project pressure, failed
  automation, and owner-only gates.
- Default views prioritize decisions, anomalies, and system movement over chat
  sessions or terminal panes.
- Session attach, recovery, and host controls remain secondary,
  capability-attested operator tools.
- Full transcripts and raw artifacts remain addressable on demand but do not
  load into the dashboard hot path.
- Command does not copy or fork public knowledge text and does not become an
  authority surface for research conclusions.

### Shared contract

Both surfaces use one typed projection contract and display the projection
version/digest. Command may enrich records privately; the public projection
never depends on Command or private overlays. A mismatch between the two views
is measurable projection drift, not an editorial choice.

The first public live-state implementation remains blocked on completion of the
first full ADR-0044 knowledge cycle. Infrastructure recovery, schema design,
redaction tests, and truthful empty states may proceed before then; fabricated
demo knowledge may not.

## Consequences

- Humans receive a credible public URL for understanding what the system knows
  and why.
- The principal receives a high-signal owner surface without duplicating the
  remote Claude/Codex launchers already available on the phone.
- Public availability and security are decoupled from the mutable runtime host.
- Knowledge interpretation has one source and two explicit disclosure levels.
- Command's existing chat and terminal investments remain useful but stop
  defining the product.

## Alternatives considered

- **Keep Synaplex as a manually written publication.** Rejected: it hides the
  system's live epistemic structure and will drift from canon.
- **Make Command the only dashboard.** Rejected: it gives outsiders no legible,
  safe view of the work.
- **Let each surface derive independently.** Rejected: duplicated projection
  logic creates silent disagreement.
- **Serve public pages directly from runtime.** Rejected: couples the public
  trust and availability boundary to hot private state.
