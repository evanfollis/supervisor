---
name: Active issues
description: Currently-live pressure on the workspace. Each entry is ≤3 lines. Historical / closed items live in `active-issues-archive.md`. Read this; load the archive on demand only.
updated: 2026-04-30
---

# Active issues

## Currently live

- **Command browser-layer verification** — server-side smoke is strong, but real-browser coverage remains a machine-owned gap. Old principal FR-0015 escalation archived; replacement handoff is `runtime/.handoff/command-browser-verification-owned-2026-04-25T1310Z.md`.
- **Synaplex site V1 deploy to synaplex.ai** — site scaffold builds clean at `projects/synaplex/site/dist/`; rebrand landed; deploy still pending. IA reshape decision open (§Open design questions in ADR-0027). Dispatched to synaplex session.
- **Synaplex loop L2/L3/L4 subsystems** — L1 intake live; Layer 2 reasoning (per-beat candidate emission), Layer 3 validation (counter-search + nightly integrity), Layer 4 presentation (writeups → site + newsletter) follow ADR-0029's bootstrap throttle (≤5 candidates/beat/day for 4 weeks).
- **Synaplex cap policy + API key** — HN queue at 409 items (cap 200); RSS at 202-204 (cap 200). Cap truncation policy unresolved (4th cycle). `ANTHROPIC_API_KEY` unprovisioned; Sonnet scorer dormant, pipeline runs heuristic-only. Both blocked on principal decision.
- **Skillfoundry agentic inbound deploy** — Preflight landing route + `sourceType` + watcher restart; Launchpad Lint + LCI landing + telemetry; ≥1 blog post/probe/week. In flight per the skillfoundry session (scope now spans `/opt/workspace/projects/skillfoundry/` root).
- **Discovery adapter post-fix findings** — 3 new findings from Codex review on `2f63ae5`: `parse_assumption` 3-claim collapse, migrate.py swallows decision-header parse failures, parse-one-file boundary leaking. Triaged per handoff; Finding B ships this cycle, Finding A proposal drafts for spec-review, Finding C's ADR promotes to accepted-pending-scheduling.
- **Canon schema — polarity surface underspecified** — Codex review on `weakens_assumption` narrow proposal rejected narrow path. Holistic audit (reconcile polarity vocabulary + coupled audit/citation/phase-0 surfaces + canon-CI gap FR-0035) dispatched to context-repo session.
- **Context-repo pass-2 retrofit** — M1+M2 retrofit for atlas landed (`49c24df` in atlas repo; 107/107 tests). skillfoundry-valuation-context retrofit proposal filed; awaiting skillfoundry session pickup.
- **INBOX saturation** — 22+ proposals in `handoffs/INBOX/` with 0 landed across 6+ synthesis cycles. All Tier-C (require `scripts/lib/` write access, attended session). Saturation exception active; `URGENT-inbox-proposal-saturation-2026-04-28T08-50Z.md` is the escalation surface. Synthesis dedup gate (Proposal 1 from 2026-04-30T03:26Z synthesis) is now also queued.
- **Synthesis output gate broken** — `synthesize.sh` produces 1-line stubs when output exceeds threshold. Last substantive synthesis was 2026-04-29T03:24Z; 2026-04-29T15:24Z was a stub. Fix is 5 lines in `scripts/lib/synthesize.sh` (Tier-C; `proposal-synthesis-output-gate-2026-04-28T03-30-01Z.md`).
- **Ghost-state: tick branches never merge to main** — FR-0038 written on main 2026-04-30. Tick wrapper creates `ticks/` branches that are never merged. 49+ unmerged branches; fixes claimed by 4 consecutive ticks were ghost-writes. Root fix requires `scripts/lib/` write access.

## Pending principal (people-or-money only)

- **Atlas hypothesis pool rotation** — pool at 12 `formulated`, ~6 days to depletion. Two BitMEX hypotheses permanently stuck in `testing` (data unavailable). Options A+C recommended (auto-promote formulated + infeasibility status). Handoff: `runtime/.handoff/general-atlas-pool-rotation-decision-needed-2026-04-29T17-00Z.md`. **24h dispatch deadline ~2026-04-30T17:00Z.**

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
