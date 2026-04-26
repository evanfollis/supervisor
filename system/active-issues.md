---
name: Active issues
description: Currently-live pressure on the workspace. Each entry is ≤3 lines. Historical / closed items live in `active-issues-archive.md`. Read this; load the archive on demand only.
updated: 2026-04-26
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

- **Atlas gate/cache misalignment (FR-0040)** — gate fires correctly on daily cadence but evaluates against potentially stale scoring data. Principal needs to decide acceptable staleness window before implementation can proceed.

## Structural / background

- **Script amendments batch — 8 INBOX proposals (Tier C)** — proposals to amend `supervisor-tick.sh`, `synthesize.sh`, `reflect.sh`, `workspace.sh` pending attended session. Includes: atomize FR creation (FR-0041 fix), synthesis output size gate (FR-0038 fix), tick invocation failure diagnostic (FR-0042 fix), governance events auto-emit, current-state commit diagnosis, workspace doctor ADR check, merge-tick-branches playbook, prior-refutation check.
- **Tick governance drift on branches (FR-0043)** — active-issues.md and FR files from tick cycles land on tick branches, not main. 6 unmerged branches. Fix direction: elevate active-issues.md to Tier-A autocommit path. Attended session required.
- **Aged tick branch with FR conflicts (doctor FAIL)** — `ticks/2026-04-20-22` aged 125h; contains FR-0035/0036/0037/0038 with different content than main — cannot be cleanly merged without manual renaming. URGENT in INBOX.
- **ADR-0031 and ADR-0032 missing review artifacts** — ADR-0031 at 6th+ reflection window without cross-agent review; ADR-0032 at 4th+. URGENT in INBOX. Attended session must write `.reviews/adr-0031-*.md` and `.reviews/adr-0032-*.md`.
- **Ghost FR recurrence (FR-0041)** — FR-0038–0040 claimed in events for 3+ consecutive ticks before landing on main. Structural fix (atomic write-verify in tick script) pending attended session. See also FR-0029 (prior recurrence).
- **Operator authority loop** — attached sessions can be executive/supervisor with repo write but no tmux/systemd host control. ADR-0015 amendment now forbids routing Evan to another "full admin" agent; repeated host-only needs must become an explicit operator bridge/tool.
- **Executive boundary discipline** — FR-0018 and follow-ons name the pattern where the executive session patches project code instead of shaping the PM layer. Ongoing; reinforced by ADR-0020 action-default + the people-or-money rubric memory.
- **ADR-0028 post-landing artifact hygiene** — artifact inbox still needs owned browser-layer proof before retiring the old `/_inbox` stopgap. Do not ask the principal for the proof path by default.
- **Workspace CLAUDE.md versioned as of `d09d2be`** — symlink from `/opt/workspace/CLAUDE.md` → `supervisor/workspace-claude.md`. All future workspace-charter edits land in git history via the supervisor repo. Autonomous-exec loop demonstrated for this change (synthesis → translator → INBOX handoff → executive commit).
- **Cowork is a secondary friction surface** — external commentary only; not a gate, validator, or backlog priority escalator. Phase D Cowork UI remains downstream of command Phase C and broader system backlog pressure. Durable contract: ADR-0032.

---

Archive for closed items: `system/active-issues-archive.md` (not auto-loaded).
