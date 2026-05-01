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
- **Headless tick 401 auth split** (FR-0039) — all headless project ticks fail with 401; interactive/reflection sessions unaffected. Root cause undiagnosed (credential source differs between headless and interactive exec paths). Operator action required.
- **reflect.sh disallow-list gap** (FR-0040) — Write and Bash(python3) not blocked in reflect.sh; a reflection session mutated HEAD on 2026-05-01. Fix: tighten disallow-list + identify auto-commit mechanism. Tier-C: attended session required.
- **Tick branch merge gap** (FR-0038) — governance artifacts (FRs, active-issues updates) written by tick sessions land on tick branches, not main. Same artifacts re-discovered each cycle. Fix: attended session merge or wrapper change to write Tier-A direct on main.
- **INBOX saturation** — 40+ proposals, oldest 149h+. All Tier-B/C (require attended session or ADR edits). Saturation exception active: no new per-proposal URGENTs. Attended session must bulk-sweep proposals or disposition the saturation URGENT.
- **Synaplex cap policy** (3rd-cycle URGENT) — ADR-0029 §6 says "max 200/source/day"; code does "max 200/fetch" with union accumulation. HN at 277+ items. Recommendation C (ratify per-fetch semantic, amend ADR-0029 §6). Score cron cadence also needs fix before API key lands (12× per day vs 3× intake runs).
- **Atlas pool rotation** — decision A+C+D2 dispatched to atlas PM via `runtime/.handoff/atlas-pool-rotation-decision.md`. Runner frozen 90h+; awaiting atlas PM pickup and execution.
- **Synthesis-to-execution pipeline stalled** — 0 of 16 proposals landed across 9 synthesis cycles. Loop is producing high-fidelity diagnosis with no execution. Requires attended session to bulk-close or accept proposals.

---

Archive for closed items: `system/active-issues-archive.md` (not auto-loaded).
