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

- **Synthesis→execution pipeline stuck (CRITICAL)** — 8 proposals from 2 synthesis cycles unlanded as of 03:24Z Apr 27. INBOX holds 15 items (3 URGENT aged 29-47h, 12 Tier-C proposals). All require attended executive session (scripts/lib/ or destructive git). Synthesis dispatch deadline 15:25Z Apr 27 expires this window. Runtime handoff: `general-synthesis-dispatch-2026-04-27T02-49Z.md`.
- **Remote push gap** — 36 commits ahead of `origin/main` (monotonically growing; was 33 at 03:24Z synthesis). Requires attended `git push` authorization. Every unattended window adds 1-3 commits.
- **Tick branch accumulation** — 10+ tick branches in supervisor repo; `ticks/2026-04-20-22` aged 157h+ (doctor WARN). Requires attended delete/merge. All tick branches from 2026-04-25 onward appear to be well-formed governance reports.
- **ADR-0031 / ADR-0032 review debt** — No cross-agent review artifacts exist. ADR-0031 at 8+ reflection windows, ADR-0032 at 6+. URGENT in INBOX (8-defer escalation). Attended session must write `.reviews/adr-0031-<iso>.md` and `.reviews/adr-0032-<iso>.md`.
- **Ghost FRs / self-reporting fabrication** — Tick events claim FR writes "on main" that are on tick branches only. `friction/` on main ends at FR-0037. Three INBOX proposals target this (atomize FR creation, tick event labeling, reflect-current-state-logging). Root cause: Tier-A writes in tick sessions commit to tick branches, not main.
- **CURRENT_STATE.md reflection-commit gate broken** — `reflect.sh:186-202` silently fails to commit CURRENT_STATE.md for synaplex (2+ cycles) and command (3+ cycles). Marked "Landed" by Apr 26 03:26Z synthesis — that was a false closure. Proposal in INBOX: `proposal-reflect-current-state-logging`.
- **Synaplex arxiv data destruction** — Adapter overwrites non-empty daily file with 0 items on stuck runs. Score corpus dropped 329→297 on Apr 26; recurred Apr 27 00:20Z. Project-level fix dispatched; CURRENT_STATE reflects proposed fix. No-clobber rule proposal in INBOX for workspace-level policy.
- **Synaplex synthesis dedup** — `synthesize.py::_gather_week` does not dedup by `content_id` across days. W17 synthesis has 2/5 slots occupied by duplicates. At 3-cycle carry-forward threshold; URGENT fires on next reflection if unaddressed.
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
