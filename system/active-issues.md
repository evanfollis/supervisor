---
name: Active issues
description: Currently-live pressure on the workspace. Each entry is ≤3 lines. Historical / closed items live in `active-issues-archive.md`. Read this; load the archive on demand only.
updated: 2026-05-02
---

# Active issues

## Currently live

- **Command browser-layer verification** — server-side smoke is strong, but real-browser coverage remains a machine-owned gap. Old principal FR-0015 escalation archived; replacement handoff is `runtime/.handoff/command-browser-verification-owned-2026-04-25T1310Z.md`.
- **Synaplex site V1 deploy to synaplex.ai** — site scaffold builds clean at `projects/synaplex/site/dist/`; rebrand landed; deploy still pending. IA reshape decision open (§Open design questions in ADR-0027). Dispatched to synaplex session.
- **Synaplex loop L2/L3/L4 subsystems** — L1 intake live; Layer 2 reasoning (per-beat candidate emission), Layer 3 validation (counter-search + nightly integrity), Layer 4 presentation (writeups → site + newsletter) follow ADR-0029's bootstrap throttle (≤5 candidates/beat/day for 4 weeks).
- **Skillfoundry agentic inbound deploy** — Preflight landing route + `sourceType` + watcher restart; Launchpad Lint + LCI landing + telemetry; ≥1 blog post/probe/week. In flight per the skillfoundry session (scope now spans `/opt/workspace/projects/skillfoundry/` root).
- **Discovery adapter post-fix findings** — 3 new findings from Codex review on `2f63ae5`: `parse_assumption` 3-claim collapse, migrate.py swallows decision-header parse failures, parse-one-file boundary leaking. Triaged per handoff; Finding B ships this cycle, Finding A proposal drafts for spec-review, Finding C's ADR promotes to accepted-pending-scheduling.
- **Canon schema — polarity surface underspecified** — Codex review on `weakens_assumption` narrow proposal rejected narrow path. Holistic audit (reconcile polarity vocabulary + coupled audit/citation/phase-0 surfaces + canon-CI gap FR-0035) dispatched to context-repo session.
- **Context-repo pass-2 retrofit** — M1+M2 retrofit for atlas landed (`49c24df` in atlas repo; 107/107 tests). skillfoundry-valuation-context retrofit proposal filed; awaiting skillfoundry session pickup.

## URGENT — principal action required

- **Headless project tick 401 auth** (FR-0039) — all project ticks failing since 2026-04-30. Reflection jobs work; tick credential path is stale. Operator fix: compare `scripts/lib/tick-*.sh` vs `workspace-reflect.timer` credential sources, rotate stale key, confirm with one manual tick run. INBOX: `URGENT-headless-tick-401-auth-2026-05-01T08-49Z.md`.
- **INBOX saturation + bulk triage** — 45+ items, 12 duplicate proposal copies, 4 URGENTs. Growing +5/synthesis cycle. Cannot be cleared autonomously (all Tier B/C). Requires attended triage session or autonomous Tier-B-auto authority grant (synthesis Proposal 5). INBOX: `URGENT-inbox-proposal-saturation-2026-04-28T08-50Z.md`.
- **LCI outreach stalled 22 days** — 10 drafts at `drafted` status; zero external evidence. Principal must decide: unblock (choose channel), park explicitly, or kill. INBOX: `URGENT-lci-outreach-blocked-22-days-2026-05-02.md`.
- **Synaplex cap policy** (4th cycle) — ADR-0029 §6 says "200/source/day"; code does "200/fetch" (HN reaches ~450/day). Recommendation: Option C (ratify per-fetch semantic, amend ADR wording — Tier A write). INBOX: `URGENT-synaplex-cap-policy-3rd-cycle-2026-05-01T14-42Z.md`.
- **Atlas runner + server maintenance** — Atlas restarted 2026-05-02T14:25Z (P0 done). P1 (TESTING re-evaluation loop) dispatched to atlas session. Server maintenance (LATEST_SYNTHESIS symlink + OS updates) in `runtime/.handoff/general-server-maintenance-2026-05-02T01-23-24Z.md`.
- **reflect.sh Write bypass** (FR-0042) — reflections write CURRENT_STATE.md in violation of read-only policy. Fix: add `"Write"` to `--disallowedTools` in `scripts/lib/reflect.sh`. Operator session required. INBOX: `reflect-sh-disallow-list-gap-2026-05-01T16-48Z.md`.

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
