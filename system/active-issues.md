---
name: Active issues
description: Currently-live pressure on the workspace. Each entry is brief; machine state belongs in verified-state.md and closed history in active-issues-archive.md.
updated: 2026-09-11T14:15Z
---

# Active issues

This is a curated pressure surface, not proof of system state. Verify every
operational claim against `system/verified-state.md` and the named project or
runtime receipt before acting. A transient item past its `recheck_by` is
unverified, not a continuing blocker.

## Time-critical

- **Command governed migration is in progress** — the restored subscription
  session is running the authoritative 18-case Claude-only release evaluation.
  Production remains on the known-good release until review, CI/CodeQL, canary,
  authenticated smoke, deployment, and rollback gates all pass. Receipt:
  `runtime/.meta/platform-recovery-2026-09-11-progress.md`; owner: executive;
  `recheck_by: 2026-09-11T14:45Z`.
- **Host reboot required after Command finishes** — the 2026-09-11 package pass
  is otherwise clean, but libc6 set `/var/run/reboot-required`. Reboot only
  after active release evidence is durable, then re-attest every surface.
  Receipt: `system/verified-state.md`; owner: operator; `recheck_by:
  2026-09-11T14:45Z`.

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
