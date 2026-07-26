# Supervisor Architecture

## Purpose

The supervisor is the durable workspace control plane. It governs repository
placement, project-session routing, decisions, verification, and host-level
operations. It does not own project business logic.

## Composition and authority

- `/opt/workspace` is the executive launch root.
- `/opt/workspace/supervisor` is the authoritative control-plane repository.
- `/opt/workspace/runtime` is generated state, telemetry, handoff, and raw-run
  storage.
- `/opt/workspace/projects/<name>` is project-session write authority.

`AGENT.md` is the canonical charter; `AGENTS.md` and `CLAUDE.md` are compatibility
symlinks. ADR-0021 still loads the declared hot context at session start.
`config/repositories.toml` is authoritative for host paths, session placement,
and canonical GitHub mappings. Each repository's `repo.toml` is authoritative
for its shape, lifecycle, risk, and optional artifact declarations.

## Dependency direction

The executive reads verified runtime evidence and durable supervisor policy,
then delegates project mutations through project sessions and provenance-checked
handoffs. Project repositories may consume published contracts or configurable
runtime paths; they do not import supervisor business logic. The supervisor may
inspect project state but is not a shared application framework.

## Artifact roles

- authoritative: `config/`, `decisions/`, `docs/`, `playbooks/`, `scripts/`,
  reviewed `system/` state, tests, and declared governance ledgers;
- runtime: `/opt/workspace/runtime`, including telemetry, handoffs, sessions,
  run artifacts, and generated status;
- generated: verified-state and other explicitly generated projections, even
  when a reviewed snapshot is retained;
- historical: `.reviews/`, accepted ADR history, archived handoffs, and
  migration receipts.

## Verification and deployment

`scripts/repository-contract.py` validates the thin ADR-0050 declaration and
front-door presence contract: metadata, declared artifact hygiene, risk
ceilings, and central-inventory divergence. It does not prove shape semantics,
instruction quality/size, artifact-list completeness, containment, deployment,
or real outcomes; profile checks and receipts own those claims. Prompt and
instruction changes follow ADR-0039. Host/service changes require capability
attestation, canaries, outcome evidence, and rollback. Current containment
exceptions and milestones live in `system/agentic-safety-gap-register.md`.
