---
name: Active issues
description: Currently-live pressure on the workspace. Each entry is ≤3 lines. Historical / closed items live in `active-issues-archive.md`. Read this; load the archive on demand only.
updated: 2026-05-01
---

# Active issues

## Currently live

- **Command browser-layer verification** — server-side smoke is strong, but real-browser coverage remains a machine-owned gap. Old principal FR-0015 escalation archived; replacement handoff is `runtime/.handoff/command-browser-verification-owned-2026-04-25T1310Z.md`.
- **Synaplex site V1 deploy to synaplex.ai** — site scaffold builds clean at `projects/synaplex/site/dist/`; rebrand landed; deploy still pending. IA reshape decision open (§Open design questions in ADR-0027). Dispatched to synaplex session.
- **Synaplex loop L2/L3/L4 subsystems** — L1 intake live; Layer 2 reasoning (per-beat candidate emission), Layer 3 validation (counter-search + nightly integrity), Layer 4 presentation (writeups → site + newsletter) follow ADR-0029's bootstrap throttle (≤5 candidates/beat/day for 4 weeks).
- **Synaplex cap policy — doc/code diverge (3rd-cycle URGENT)** — ADR-0029 §6 says max-200/source/day; implementation does max-200/fetch with union accumulation (HN reaching ~400/day). URGENT in INBOX. Recommendation C (ratify per-fetch semantic, amend ADR). Also: score cron fires 12× vs 3× intake — 9 wasted runs when API key lands. Both need attended executive decision.
- **Skillfoundry agentic inbound deploy** — Preflight landing route + `sourceType` + watcher restart; Launchpad Lint + LCI landing + telemetry; ≥1 blog post/probe/week. In flight per the skillfoundry session (scope now spans `/opt/workspace/projects/skillfoundry/` root).
- **Discovery adapter post-fix findings** — 3 new findings from Codex review on `2f63ae5`: `parse_assumption` 3-claim collapse, migrate.py swallows decision-header parse failures, parse-one-file boundary leaking. Triaged per handoff; Finding B ships this cycle, Finding A proposal drafts for spec-review, Finding C's ADR promotes to accepted-pending-scheduling.
- **Canon schema — polarity surface underspecified** — Codex review on `weakens_assumption` narrow proposal rejected narrow path. Holistic audit (reconcile polarity vocabulary + coupled audit/citation/phase-0 surfaces + canon-CI gap FR-0035) dispatched to context-repo session.
- **Context-repo pass-2 retrofit** — M1+M2 retrofit for atlas landed (`49c24df` in atlas repo; 107/107 tests). skillfoundry-valuation-context retrofit proposal filed; awaiting skillfoundry session pickup.
- **Atlas pool rotation — decision written, awaiting execution** — A+C+D2 decision written to `runtime/.handoff/atlas-pool-rotation-decision.md` 2026-05-01T18:47Z. Atlas PM to execute: auto-promote INFEASIBLE (A+C), fallback-to-formulated with confirmed-data-source check (D2). Runner frozen 90h+ pending this.
- **Headless tick 401 auth (FR-0039)** — all scheduled project ticks failing with 401; interactive sessions unaffected. Root cause undiagnosed. Operator action required (check env vs keychain credential source). See URGENT in INBOX and FR-0039.
- **reflect.sh disallow-list gap (FR-0040)** — Write tool not blocked in reflection sessions; skillfoundry-harness reflection mutated HEAD. Also: unidentified host process runs git-commit commands embedded in CURRENT_STATE.md. Fix requires Tier-C write to scripts/lib/reflect.sh. See INBOX routing item.
- **Tick branch governance gap (FR-0038)** — tick sessions write governance artifacts (FR files, active-issues updates) on tick branches that are never merged to main. Artifacts are siloed and get re-discovered/re-reported each cycle. Requires structural playbook or merge automation.
- **INBOX saturation — 30+ proposals without disposition** — Synthesis proposals from 2026-04-25 onward (some 147h old) have no attended disposition. Saturation exception applies; no new per-proposal URGENTs. Attended executive must bulk-close or accept the queue.

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
