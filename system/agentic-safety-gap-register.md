# Agentic Safety Gap Register

Updated: 2026-07-26
Authority: ADR-0050
Owner: workspace executive/operator

This is the live transition register between the July 2026 agentic-safety
baseline and the observed host. An entry is not a waiver of the target. It is a
bounded, dated exception that makes current exposure and the next control
explicit while migrations remain reversible.

## Open exceptions

### ASG-001 — Shared root execution identity

- Status: open
- Applies to: workspace session fabric and project services that do not declare
  a non-root `User=`
- Observed: the executive/project sessions and most inspected hosted units run
  as root
- Exposure: model-controlled processes can reach a wider host and workspace
  surface than their project task requires
- Existing controls: project-session authority boundaries, handoff provenance,
  Git ownership, selected systemd filesystem restrictions, and human-auditable
  session traces
- Owner: workspace operator
- Milestone: approve a dedicated identity-and-sandbox migration ADR with unit
  inventory, ownership map, credential-broker boundary, and recovery plan
- Target date: 2026-08-09
- Exit evidence: canary project resumes, checks, deploys, rolls back, and loses
  unauthorized cross-project/host access under a dedicated identity

### ASG-002 — Incomplete filesystem, process, and network containment

- Status: open
- Applies to: agentic/model-assisted services and persistent sessions
- Observed: protection directives are inconsistent; default-deny network and
  process boundaries are not fleet-wide
- Exposure: a long-running agent can search laterally for infrastructure or
  package/proxy weaknesses beyond its intended sandbox
- Existing controls: only selected units use `ProtectSystem`, explicit write
  paths, or related systemd restrictions; `make runtime-audit` now inventories
  the live workspace-related units and emits severity-ranked, machine-readable
  findings without changing them
- Owner: workspace operator
- Milestone: inventory every active unit, assign a containment profile, and
  canary restrictions on one read-only and one stateful service
- Target date: 2026-08-09
- Exit evidence: automated negative tests prove denied filesystem, process,
  device, socket, and network capabilities; required work still succeeds

### ASG-003 — Ambient credentials instead of scoped capability brokerage

- Status: open
- Applies to: provider, GitHub, deploy, signing, and host-control credentials
- Observed: parts of the current fabric rely on ambient/shared credential
  availability rather than per-task issuance
- Exposure: sandbox escape or prompt/tool compromise can inherit authority
  unrelated to the task
- Existing controls: provider-specific environment handling and scoped workflow
  permissions in some repositories
- Owner: workspace operator
- Milestone: document credential consumers and introduce one brokered,
  expiring, revocable capability canary with secrets outside model-visible
  execution
- Target date: 2026-08-16
- Exit evidence: task succeeds with the scoped capability; revoked/expired and
  unrelated capabilities fail without exposing secret material

### ASG-004 — Uneven trajectory and outcome evidence

- Status: open
- Applies to: every `agentic` repository and relevant `model-assisted` surface
- Observed: telemetry, prompt evals, durable run identity, and real-outcome
  verification exist unevenly across the hosted fleet
- Exposure: successful completion text or a locally valid step can hide a
  harmful long trajectory, failed external outcome, or unsafe resume
- Existing controls: prompt-eval substrate, project tests, handoff provenance,
  selected deployment receipts, and supervisor telemetry
- Owner: workspace executive plus each project owner
- Milestone: each repository declares run/session identity, outcome witness,
  trace retention, resume semantics, and incident-derived regression cases in
  its migration
- Target date: repository-specific; required before that repository is marked
  conforming
- Exit evidence: clean `make check`, prompt/agent eval gate where applicable,
  abort/resume test, and an externally verified outcome receipt

### ASG-005 — EOL system Node.js runtime

- Status: open
- Applies to: host services whose installed units execute `/usr/bin/node`
- Observed: `/usr/bin/node` is v20.20.2 while the interactive/build toolchain
  resolves v22.22.0; `command.service` explicitly executes `/usr/bin/node`.
  Node.js 20 reached EOL on 2026-03-24, while Node.js 24 is the current LTS
  production line according to the official release schedule.
- Exposure: production behavior and vulnerability support differ from CI/build
  behavior, and an EOL runtime no longer receives normal upstream fixes
- Existing controls: repository build/type/auth gates, immutable Command
  releases, and rollback to the prior installed unit/release
- Owner: workspace operator
- Milestone: inventory every `/usr/bin/node` consumer, package Node.js 24 LTS
  outside root-owned NVM state, then canary and roll back each service
  independently before changing the host default
- Target date: 2026-08-02
- Exit evidence: per-service tests and outcome receipts run under the exact
  installed Node.js 24 binary; rollback is exercised; no active workspace unit
  remains on Node.js 20
- Reference: https://nodejs.org/en/about/previous-releases

## Closed exceptions

None.

## Review rule

Review this register whenever a repository is marked conforming, a capability
is expanded, an agentic incident or near miss occurs, or a target date passes.
Closing an entry requires evidence; changing its scope or date requires a
recorded reason.
