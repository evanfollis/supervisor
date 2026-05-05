---
name: Active issues
description: Currently-live pressure on the workspace. Each entry is ≤3 lines. Historical / closed items live in `active-issues-archive.md`. Read this; load the archive on demand only.
updated: 2026-05-05
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

## Pending principal (people-or-money only)

- None currently. External-service setup should first be converted to a
  machine-owned fallback path before being treated as principal work.

## Structural / background

- **Tick branch governance isolation (FR-0038, CRITICAL)** — All tick-written Tier-A artifacts (FR files, active-issues, verified-state) commit to tick branches never merged to main. Doctor shows 8 branches >72h, 24 >24h. FR-0038/0039/0040 exist only on orphan branches; main shows FR-0037 as latest. Attended session must merge or cherry-pick tick branches + add merge playbook.
- **LATEST_SYNTHESIS stub (CRITICAL)** — `cross-cutting-2026-05-05T03-23-14Z.md` is 67 bytes (only its own path). Synthesis output is broken. Fix is in `scripts/lib/synthesize.sh` (Tier C); proposal-latest-synthesis-pointer in INBOX cycle 2.
- **reflect.sh Write bypass (FR-0040)** — `scripts/lib/reflect.sh` missing `"Write"` in disallowedTools; 11 cycles unfixed; Tier C change. One inadvertent commit confirmed 2026-05-01. 1-line fix blocked behind INBOX saturation.
- **LCI outreach stalled 22+ days** — 10 drafts at `drafted` since 2026-04-11; principal decision needed (channel + Tally form or park/kill). URGENT in INBOX since 2026-05-02.
- **Synaplex cap policy** — doc/code diverge on cap semantics; 3rd-cycle URGENT in INBOX. Scoring cron may waste API calls once ANTHROPIC_API_KEY lands.
- **INBOX proposal saturation** — 44+ proposals (Tier B/C) since 2026-04-25; saturation URGENT filed 2026-04-28, still open. Attended session must bulk-disposition or archive.
- **Operator authority loop** — attached sessions can be executive/supervisor — attached sessions can be executive/supervisor
  with repo write but no tmux/systemd host control. ADR-0015 amendment now
  forbids routing Evan to another "full admin" agent; repeated host-only needs
  must become an explicit operator bridge/tool.
- **Executive boundary discipline** — FR-0018 and follow-ons name the pattern where the executive session patches project code instead of shaping the PM layer. Ongoing; reinforced by ADR-0020 action-default + the people-or-money rubric memory.
- **ADR-0028 post-landing artifact hygiene** — artifact inbox still needs owned browser-layer proof before retiring the old `/_inbox` stopgap. Do not ask the principal for the proof path by default.
- **Workspace CLAUDE.md versioned as of `d09d2be`** — symlink from `/opt/workspace/CLAUDE.md` → `supervisor/workspace-claude.md`. All future workspace-charter edits land in git history via the supervisor repo. Autonomous-exec loop demonstrated for this change (synthesis → translator → INBOX handoff → executive commit).
- **Cowork is a secondary friction surface** — external commentary only; not a gate, validator, or backlog priority escalator. Phase D Cowork UI remains downstream of command Phase C and broader system backlog pressure. Durable contract: ADR-0032.

---

Archive for closed items: `system/active-issues-archive.md` (not auto-loaded).
