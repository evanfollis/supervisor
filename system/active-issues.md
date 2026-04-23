---
name: Active issues
description: Currently-live pressure on the workspace. Each entry is ≤3 lines. Historical / closed items live in `active-issues-archive.md`. Read this; load the archive on demand only.
updated: 2026-04-23
---

# Active issues

## Currently live

- **Context-always-load 30KB cap collision** — aggregate was ~49KB before this trim; active-issues.md alone was 24KB (80% of budget). Trimming in progress (this commit). Per-file target ≤5KB; aggregate target ≤25KB leaving margin. Follow-on: adopt Anthropic memory tool + prompt-caching structure per ADR-0030 (proposed).
- **Phase C command UX** — C1 read-only streaming attach live at `/attach/<name>`; C2 (write path + writer lock + reconnect) in flight per `runtime/.handoff/command-phase-c2-kickoff-2026-04-23T19-15Z.md`. C3 (ephemeral pool + reasoning UI + attach picker) follows. D (Cowork panels) parked until C lands and is used ≥3 days.
- **Synaplex site V1 deploy to synaplex.ai** — site scaffold builds clean at `projects/synaplex/site/dist/`; rebrand landed; deploy still pending. IA reshape decision open (§Open design questions in ADR-0027). Dispatched to synaplex session.
- **Synaplex loop L2/L3/L4 subsystems** — L1 intake live; Layer 2 reasoning (per-beat candidate emission), Layer 3 validation (counter-search + nightly integrity), Layer 4 presentation (writeups → site + newsletter) follow ADR-0029's bootstrap throttle (≤5 candidates/beat/day for 4 weeks).
- **Skillfoundry agentic inbound deploy** — Preflight landing route + `sourceType` + watcher restart; Launchpad Lint + LCI landing + telemetry; ≥1 blog post/probe/week. In flight per the skillfoundry session (scope now spans `/opt/workspace/projects/skillfoundry/` root).
- **Discovery adapter post-fix findings** — 3 new findings from Codex review on `2f63ae5`: `parse_assumption` 3-claim collapse, migrate.py swallows decision-header parse failures, parse-one-file boundary leaking. Triaged per handoff; Finding B ships this cycle, Finding A proposal drafts for spec-review, Finding C's ADR promotes to accepted-pending-scheduling.
- **Canon schema — polarity surface underspecified** — Codex review on `weakens_assumption` narrow proposal rejected narrow path. Holistic audit (reconcile polarity vocabulary + coupled audit/citation/phase-0 surfaces + canon-CI gap FR-0035) dispatched to context-repo session.
- **Context-repo pass-2 retrofit** — M1+M2 retrofit for atlas landed (`49c24df` in atlas repo; 107/107 tests). skillfoundry-valuation-context retrofit proposal filed; awaiting skillfoundry session pickup.

## Pending principal (people-or-money only)

- **Tally form embed for LCI** (~5 min; form creation is the blocker; cost unchanged at $99 listing price) — `runtime/.handoff/general-skillfoundry-tally-form-needed-2026-04-18.md`.
- **Kernel reboot** — 6.8.0-110 installed since 2026-04-15; running 6.8.0-107. Low urgency; reversible via tmux-session respawn machinery.

## Structural / background

- **Executive boundary discipline** — FR-0018 and follow-ons name the pattern where the executive session patches project code instead of shaping the PM layer. Ongoing; reinforced by ADR-0020 action-default + the people-or-money rubric memory.
- **ADR-0028 post-landing artifact hygiene** — stale `runtime/.handoff/URGENT-command-fr0015-principal-decision-needed.md` still on disk; command session to verify closure and delete OR escalate if genuinely open.
- **Workspace CLAUDE.md versioned as of `d09d2be`** — symlink from `/opt/workspace/CLAUDE.md` → `supervisor/workspace-claude.md`. All future workspace-charter edits land in git history via the supervisor repo. Autonomous-exec loop demonstrated for this change (synthesis → translator → INBOX handoff → executive commit).

---

Archive for closed items: `system/active-issues-archive.md` (not auto-loaded).
