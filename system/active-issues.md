---
name: Active issues
description: Currently-live pressure on the workspace. Each entry is ≤3 lines. Historical / closed items live in `active-issues-archive.md`. Read this; load the archive on demand only.
updated: 2026-04-30
---

# Active issues

## Currently live

- **Atlas hypothesis pool rotation — principal decision needed** — Runner stuck on 2 BitMEX-dependent `testing` hypotheses (no data); 12 `formulated` hypotheses never pulled into testing; 9 all-continue streak; pool depletes in ~6 days. Options A+C (auto-promote with feasibility check + add INFEASIBLE status) recommended by atlas PM. Handoff: `runtime/.handoff/general-atlas-pool-rotation-decision-needed-2026-04-29T17-00Z.md` (~12h old; 24h dispatch obligation approaching).
- **INBOX saturation + synthesis loop broken** — 25 Tier-B/C proposals in INBOX aged 24–103h; 0 of 12 synthesis proposals landed across 6 synthesis cycles. Synthesis output gate broken (stubs); 3 new duplicates from translator at 03:35Z. Saturation exception active. All items require attended session. URGENT: `handoffs/INBOX/URGENT-inbox-proposal-saturation-2026-04-28T08-50Z.md`.
- **Tick-branch ghost-state (FR-0038)** — Tick sessions write Tier-A changes to tick branches that are never merged to main. Events claim "on main"; main didn't receive commits. `active-issues.md` was stale from 2026-04-25; FR-0038 claimed 3 times, never landed. Requires `scripts/lib/` fix (Tier-C, attended session). FR-0038 first genuinely filed this tick.
- **LATEST_SYNTHESIS pointer broken** — symlink writes through to cross-cutting file; synthesize.sh writes stubs when output is large; last substantive synthesis was 2026-04-29T03:24Z. Repair needed in `scripts/lib/synthesize.sh` (Tier-C). Server maintenance handoff: `runtime/.handoff/general-server-maintenance-2026-04-30T01-24-05Z.md`.
- **Tick branch proliferation** — 49+ tick branches unmerged; 13 >72h (doctor FAIL), 22+ >24h. Rate ~3/12h; will exceed 100 in ~7 days. Root: tick wrapper never merges to main. Playbook proposal in INBOX (`proposal-merge-tick-branches-playbook-2026-04-26T03-37-07Z.md`).
- **Command browser-layer verification** — server-side smoke is strong, but real-browser coverage remains a machine-owned gap. Old principal FR-0015 escalation archived; replacement handoff is `runtime/.handoff/command-browser-verification-owned-2026-04-25T1310Z.md`.
- **Synaplex site V1 deploy to synaplex.ai** — site scaffold builds clean at `projects/synaplex/site/dist/`; rebrand landed; deploy still pending. IA reshape decision open (§Open design questions in ADR-0027). Dispatched to synaplex session.
- **Synaplex loop L2/L3/L4 subsystems** — L1 intake live; Layer 2 reasoning (per-beat candidate emission), Layer 3 validation (counter-search + nightly integrity), Layer 4 presentation (writeups → site + newsletter) follow ADR-0029's bootstrap throttle (≤5 candidates/beat/day for 4 weeks). Cap truncation policy unresolved (4th cycle); ANTHROPIC_API_KEY unprovisioned (Sonnet scorer dormant).
- **Skillfoundry agentic inbound deploy** — Preflight landing route + `sourceType` + watcher restart; Launchpad Lint + LCI landing + telemetry; ≥1 blog post/probe/week. In flight per the skillfoundry session (scope now spans `/opt/workspace/projects/skillfoundry/` root).
- **Discovery adapter post-fix findings** — 3 new findings from Codex review on `2f63ae5`: `parse_assumption` 3-claim collapse, migrate.py swallows decision-header parse failures, parse-one-file boundary leaking. Triaged per handoff; Finding B ships this cycle, Finding A proposal drafts for spec-review, Finding C's ADR promotes to accepted-pending-scheduling.
- **Canon schema — polarity surface underspecified** — Codex review on `weakens_assumption` narrow proposal rejected narrow path. Holistic audit (reconcile polarity vocabulary + coupled audit/citation/phase-0 surfaces + canon-CI gap FR-0035) dispatched to context-repo session.
- **Context-repo pass-2 retrofit** — M1+M2 retrofit for atlas landed (`49c24df` in atlas repo; 107/107 tests). skillfoundry-valuation-context retrofit proposal filed; awaiting skillfoundry session pickup.

## Pending principal (people-or-money only)

- **Atlas pool rotation decision** — Options A/B/C/A+C for hypothesis pool rotation; principal input required before implementation. See handoff at `runtime/.handoff/general-atlas-pool-rotation-decision-needed-2026-04-29T17-00Z.md`.

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
