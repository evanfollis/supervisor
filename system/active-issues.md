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
- **Synaplex arxiv adapter data-destruction** [CRITICAL] — adapter overwrites daily file with 0 items on stuck runs; corpus lost 32 items in 2026-04-26 cycle. Dispatched to synaplex session via `runtime/.handoff/synaplex-arxiv-data-destruction-2026-04-27T04-48Z.md`. Synaplex dedup bug at 3-cycle carry-forward threshold (same dispatch).
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
- **Tick event labeling bug (FR-0038)** [CRITICAL] — tick events hard-code "main" as artifact location; commits land on tick branches. Root cause of ghost FRs, branch stranding, stale active-issues on main. Fix: `supervisor-tick.sh` must capture `ACTUAL_BRANCH` at commit time. Requires attended session edit. Fix dispatched via `runtime/.handoff/general-synthesis-dispatch-2026-04-27T02-49Z.md`.
- **INBOX saturation + synthesis dispatch deadline** [HIGH] — 15 INBOX items, 3 URGENTs aged 37h+, 0/8 synthesis proposals landed across 2 cycles. 2026-04-26T15:25Z synthesis deadline is **2026-04-27T15:25Z** (8.5h from 06:48Z tick). Attended session must act or record explicit deferral. See `runtime/.handoff/general-synthesis-dispatch-2026-04-27T02-49Z.md`.
- **Tick branch cleanup** [WARN] — `ticks/2026-04-20-22` aged 151h (doctor FAIL). 8 branches aged >24h (warn). Attended session must delete/merge. Remote push gap: 36 commits ahead of origin/main.
- **ADR-0031 and ADR-0032 review debt** [URGENT, 9 defers] — no cross-agent review artifacts written. Required: `.reviews/adr-0031-<iso>.md` and `.reviews/adr-0032-<iso>.md`. See INBOX `URGENT-escalated-adr-review-and-tick-branch-8-defers-2026-04-26T08-48Z.md`.
- **CURRENT_STATE.md reflection-commit gate failing** — synaplex and command CURRENT_STATE.md uncommitted across 3 consecutive cycles. `reflect.sh:186-202` silently fails. Fix dispatched via synthesis proposals; requires attended session edit to `reflect.sh`.

---

Archive for closed items: `system/active-issues-archive.md` (not auto-loaded).
