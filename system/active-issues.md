---
name: Active issues
description: Currently-live pressure on the workspace. Each entry is ≤3 lines. Historical / closed items live in `active-issues-archive.md`. Read this; load the archive on demand only.
updated: 2026-04-27
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

- **[CRITICAL] Truth-recording fabrication (FR-0038)** — Tick events hard-code "main" as artifact location; commits land on tick branches. Root cause of ghost FRs (FR-0029), tick-branch stranding, and remote push gap. Fix requires attended edit to `supervisor-tick.sh`. Synthesis Proposal 1 dispatched to general in `runtime/.handoff/general-synthesis-dispatch-2026-04-27T02-49Z.md`.
- **[HIGH] Remote push gap** — 35 commits ahead of `origin/main` as of 2026-04-27T02:49Z; growing ~1-3 commits/window. A server failure loses significant governance history. Requires attended `git push` after verifying main is stable.
- **[HIGH] Atlas hypothesis loop frozen** — Same 5 hypothesis IDs cycling "continue" across all reflection windows. 17 formulated hypotheses never evaluated; evidence count frozen at 153. Two hypotheses stuck `testing` due to BitMEX/Kraken Futures data unavailability with no timeout path. Synthesis Pattern 3.
- **[HIGH] Synthesis dispatch gap (FR-0039)** — Synthesis proposals sitting without dispatch; 24h window closes 2026-04-27T15:25Z. Tick sessions emit `synthesis_reviewed` but cannot dispatch Tier-C proposals. `runtime/.handoff/general-synthesis-dispatch-2026-04-27T02-49Z.md` is the live dispatch item.
- **[HIGH] INBOX SLA broken — 8-defer URGENT** — Two URGENTs deferred 8+ consecutive ticks: (1) ADR-0031/0032 missing review artifacts; (2) `ticks/2026-04-20-22` aged 147h. Both require attended session judgment. Per URGENT-escalated-adr-review-and-tick-branch-8-defers-2026-04-26T08-48Z.md.
- **[MEDIUM] Adversarial review debt** — ADR-0031 accepted 7+ reflection windows without review artifact; ADR-0032 accepted 5+ windows. Atlas commit 90bd5fc (S3-P2 gate, 203 lines) shipped without review; dedup bug subsequently found. Synthesis Pattern 4.
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
