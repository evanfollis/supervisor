---
name: Active issues
description: Currently-live pressure on the workspace. Each entry is ≤3 lines. Historical / closed items live in `active-issues-archive.md`. Read this; load the archive on demand only.
updated: 2026-05-02
---

# Active issues

## URGENT — requires attended session or operator action

- **[OPERATOR] Headless project tick 401 auth failure** — All project ticks failing with `401 Invalid authentication credentials` since ~2026-04-30. Reflections work (different credential path). Operator action: compare tick vs. reflect credential sources, rotate stale key. FR-0039 (origin/main). INBOX: `URGENT-headless-tick-401-auth-2026-05-01T08-49Z.md`. Operator bundle: `runtime/.handoff/general-operator-actions-required-2026-05-02T06-48Z.md`.
- **[OPERATOR] Atlas runner undeployed** — S3-P2 fix (39b6d2f, 156/156 tests) on main; `atlas-runner.service` not restarted. `sudo systemctl restart atlas-runner.service`. Handoff: `runtime/.handoff/general-atlas-s3p2-restart-needed-2026-05-02T04-47Z.md`.
- **[PRINCIPAL] LCI outreach blocked 22 days** — 10 drafts at `drafted` status since 2026-04-11. 3-cycle carry-forward threshold crossed. Decision required: unblock (Tally form + channel), park, or kill LCI lane. INBOX: `URGENT-lci-outreach-blocked-22-days-2026-05-02.md`.
- **[PRINCIPAL] Synaplex cap policy — 4th cycle** — ADR-0029 §6 says "max 200/source/day"; implementation does "max 200/fetch" with union accumulation. Option C (ratify per-fetch, amend ADR wording) recommended. INBOX: `URGENT-synaplex-cap-policy-3rd-cycle-2026-05-01T14-42Z.md`.
- **[PRINCIPAL] INBOX bulk triage** — 40+ proposals, 11 synthesis cycles, 0 landed. Saturation exception active. Requires attended bulk disposition. INBOX: `URGENT-inbox-proposal-saturation-2026-04-28T08-50Z.md`.
- **[CRITICAL] Ghost-write false verification** — Tick sessions emit explicit "verified on disk" claims that are empirically false. FR-0040. Active blocks: active-issues.md frozen at 2026-04-25 through 7 ticks; FR-0038/0039 claimed but not on local main (exist on origin/main only). Root cause: tick branch isolation + reference-frame error in verification logic.
- **[STRUCTURAL] Local main / origin/main divergence** — Local main is ~35 commits ahead of origin/main with different FR numbering. origin/main has `FR-0038-consecutive-tick-invocation-failures.md` and `FR-0039-fr-ghost-write-tick-branch-isolation.md`; local main has neither. Reconciliation required at attended session.

## Currently live

- **Command browser-layer verification** — server-side smoke is strong, but real-browser coverage remains a machine-owned gap. Old principal FR-0015 escalation archived; replacement handoff is `runtime/.handoff/command-browser-verification-owned-2026-04-25T1310Z.md`.
- **Synaplex site V1 deploy to synaplex.ai** — site scaffold builds clean at `projects/synaplex/site/dist/`; rebrand landed; deploy still pending. IA reshape decision open (§Open design questions in ADR-0027). Dispatched to synaplex session.
- **Synaplex loop L2/L3/L4 subsystems** — L1 intake live; Layer 2 reasoning (per-beat candidate emission), Layer 3 validation (counter-search + nightly integrity), Layer 4 presentation (writeups → site + newsletter) follow ADR-0029's bootstrap throttle (≤5 candidates/beat/day for 4 weeks).
- **Skillfoundry agentic inbound deploy** — Preflight landing route + `sourceType` + watcher restart; Launchpad Lint + LCI landing + telemetry; ≥1 blog post/probe/week. In flight per the skillfoundry session (scope now spans `/opt/workspace/projects/skillfoundry/` root).
- **Discovery adapter post-fix findings** — 3 new findings from Codex review on `2f63ae5`: `parse_assumption` 3-claim collapse, migrate.py swallows decision-header parse failures, parse-one-file boundary leaking. Triaged per handoff; Finding B ships this cycle, Finding A proposal drafts for spec-review, Finding C's ADR promotes to accepted-pending-scheduling.
- **Canon schema — polarity surface underspecified** — Codex review on `weakens_assumption` narrow proposal rejected narrow path. Holistic audit (reconcile polarity vocabulary + coupled audit/citation/phase-0 surfaces + canon-CI gap FR-0035) dispatched to context-repo session.
- **Context-repo pass-2 retrofit** — M1+M2 retrofit for atlas landed (`49c24df` in atlas repo; 107/107 tests). skillfoundry-valuation-context retrofit proposal filed; awaiting skillfoundry session pickup.

## Pending principal (people-or-money only)

- None currently. External-service setup should first be converted to a
  machine-owned fallback path before being treated as principal work.

## Structural / background

- **Operator authority loop** — attached sessions can be executive/supervisor
  with repo write but no tmux/systemd host control. ADR-0015 amendment now
  forbids routing Evan to another "full admin" agent; repeated host-only needs
  must become an explicit operator bridge/tool.
- **Executive boundary discipline** — FR-0018 and follow-ons name the pattern where the executive session patches project code instead of shaping the PM layer. Ongoing; reinforced by ADR-0020 action-default + the people-or-money rubric memory.
- **ADR-0028 post-landing artifact hygiene** — artifact inbox still needs owned browser-layer proof before retiring the old `/_inbox` stopgap. Do not ask the principal for the proof path by default.
- **Workspace CLAUDE.md versioned as of `d09d2be`** — symlink from `/opt/workspace/CLAUDE.md` → `supervisor/workspace-claude.md`. All future workspace-charter edits land in git history via the supervisor repo. Autonomous-exec loop demonstrated for this change (synthesis → translator → INBOX handoff → executive commit).
- **Cowork is a secondary friction surface** — external commentary only; not a gate, validator, or backlog priority escalator. Phase D Cowork UI remains downstream of command Phase C and broader system backlog pressure. Durable contract: ADR-0032.

---

Archive for closed items: `system/active-issues-archive.md` (not auto-loaded).
