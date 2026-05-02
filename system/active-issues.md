---
name: Active issues
description: Currently-live pressure on the workspace. Each entry is ≤3 lines. Historical / closed items live in `active-issues-archive.md`. Read this; load the archive on demand only.
updated: 2026-05-02
---

# Active issues

## URGENT (operator or principal action required)

- **[OPERATOR] Headless project tick 401 auth** — all project ticks failing since 2026-04-30; reflection jobs unaffected. Credential path divergence. FR-0039. `handoffs/INBOX/URGENT-headless-tick-401-auth-2026-05-01T08-49Z.md`.
- **[OPERATOR] Atlas runner not restarted** — S3-P2 gate fix `39b6d2f` deployed to main but atlas-runner.service not restarted; 14+ empty cycles, self-escalation gate broken. `runtime/.handoff/general-operator-actions-required-2026-05-02T06-48Z.md`.
- **[PRINCIPAL] LCI outreach blocked 22 days** — 10 drafts at `drafted` since 2026-04-11; channel decision needed (Tally form, outreach method, or park/kill). `handoffs/INBOX/URGENT-lci-outreach-blocked-22-days-2026-05-02.md`.
- **[PRINCIPAL] Synaplex cap policy** — ADR-0029 §6 doc/code diverge (200/day vs 200/fetch+union). Recommendation: option C (ratify per-fetch, amend ADR wording). 24h deadline expired. `handoffs/INBOX/URGENT-synaplex-cap-policy-3rd-cycle-2026-05-01T14-42Z.md`.
- **[PRINCIPAL] INBOX saturation** — 49+ items (18 duplicates, 4 URGENTs), growing +5/cycle; saturation URGENT is 105h old without triage. Tick sessions cannot clear it. Dispatch pipeline broken (0/40 proposals implemented in 11 cycles, FR-0041). `handoffs/INBOX/URGENT-inbox-proposal-saturation-2026-04-28T08-50Z.md`.

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

- **Ghost-write / tick false verification** — headless tick sessions claim to write FR records and update active-issues.md but files never land on disk (FR-0037 was highest on disk until this tick; 0038-0042 ghost-written 10+ times). Proposal: post-action verification in tick wrapper. `handoffs/INBOX/proposal-post-action-state-verify-2026-05-02T15-31-58Z.md`. FR-0040.
- **reflect.sh Write bypass** — reflection sessions mutate CURRENT_STATE.md via Write tool (not in disallow list); one reflection-embedded git command executed unauthorized commit. Fix is additive (add "Write" to disallow list). FR-0042. `handoffs/INBOX/reflect-sh-disallow-list-gap-2026-05-01T16-48Z.md`.
- **Synthesis execution gap** — 11 synthesis cycles, 0/40 proposals implemented. All proposals require Tier-C edits (scripts/lib/, CLAUDE.md). New Proposal 5: Tier-B-auto authority for additive workspace-infrastructure fixes. FR-0041. `handoffs/INBOX/proposal-tier-b-auto-authority-2026-05-02T18-50Z.md`.
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
