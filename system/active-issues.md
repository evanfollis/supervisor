---
name: Active issues
description: Currently-live pressure on the workspace. Each entry is brief; machine state belongs in verified-state.md and closed history in active-issues-archive.md.
updated: 2026-09-11T15:38Z
---

# Active issues

This is a curated pressure surface, not proof of system state. Verify every
operational claim against `system/verified-state.md` and the named project or
runtime receipt before acting. A transient item past its `recheck_by` is
unverified, not a continuing blocker.

## Time-critical

- **Command governed migration is quota-paused, not bypassed** — the
  authoritative replacement run failed closed at holdout case 16 when Claude
  reached its session limit; 153 Claude calls succeeded, the Claude throttle
  was recorded, and Codex fallback was denied. The accepted baseline was not
  changed. Capacity reports a reset at 18:20 UTC. A narrow Next security hotfix
  is independently deployed at `8b576c1`; the migration still requires a wholly
  fresh 18-case run plus every review/release gate. Receipt:
  `runtime/.meta/platform-recovery-2026-09-11-progress.md`; owner: executive;
  `recheck_by: 2026-09-11T18:25Z`.
- **Host reboot is ready now** — the active eval has stopped, production is on
  a verified immutable hotfix, and both main and candidate commit history are
  durable. libc6 still requires reboot; re-attest every surface afterward.
  Receipt: `system/verified-state.md`; owner: operator; `recheck_by:
  2026-09-11T16:00Z`.

## Product and methodology pressure

- **Synaplex produces no findings yet** — operations and publication are live,
  while artifact-delivery v2 remains quarantined and the exploratory v3 method
  was rejected pre-entry. The next admissible successor must correct the eight
  methodological defects recorded in Synaplex `CURRENT_STATE.md`.
- **Atlas remains intentionally parked** — do not restart autonomous execution
  until its data-lineage and hypothesis-dedup acceptance criteria are met. A
  healthy dormant pod is preferable to ungrounded activity.
- **Private credential remediation is owner-secure work** — provider/database
  credentials were identified in the 2026-07-27 private-boundary audit. Their
  present validity/remediation state is unverified; the principal must verify
  provider state before any rotation or private-history work. Receipt:
  `runtime/.handoff/general-public-portfolio-private-boundary-audit-2026-07-27.md`.

## Control-plane pressure

- **Prompt governance is incomplete** — `prompteval check` passes the two
  governed prompts but still identifies 20 ungoverned instruction/prompt
  surfaces. Treat this as bounded coverage, not platform-wide prompt proof.
- **Model-work admission remains implicit** — expensive release evaluations
  compete for subscription capacity. Continue serializing authoritative release
  evals until measured evidence supports a broader concurrency budget.
- **External account state is partly unobservable from the host** — registrar,
  Render marketplace, and billing details require provider-side evidence. The
  administrative register must never be treated as a live-status projection.

## Explicitly not active pressure

- The stale Supervisor tick branch and saturated handoff queue are reconciled.
- Synaplex dependency alerts are closed and its production release is current.
- Retired Mentor/Recruiter/autodeploy surfaces are not recovery targets.
- Read-only reflection sessions no longer create M5 state-drift handoff noise.
