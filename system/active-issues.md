---
name: Active issues
description: Currently-live pressure on the workspace. Each entry is ≤3 lines. Historical / closed items live in `active-issues-archive.md`. Read this; load the archive on demand only.
updated: 2026-04-25
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
- **ADR-0031 / ADR-0032 missing cross-agent reviews** — both accepted without review artifacts; 5 and 3 reflection windows past threshold. URGENT in INBOX (`URGENT-adr-review-gap-0031-0032-routed`). Write `.reviews/adr-0031-*.md` and `.reviews/adr-0032-*.md` in attended session.
- **Synthesis job writing empty stubs (FR-0038)** — two consecutive synthesis runs (03:27 and 15:28 Apr 25) produced 67-byte output containing only the file path. Downstream translator filed INBOX proposals from the empty stub; provenance suspect. Root cause unknown; `scripts/lib/workspace-synthesize.sh` output capture likely culprit. URGENT in INBOX.
- **Tick branches not merging to main** — `ticks/2026-04-20-22` (118h+, doctor FAIL) and `ticks/2026-04-25-16` / `ticks/2026-04-25-18` contain unmerged Tier-A Tier-B work. Active-issues updates and FR records from those ticks are invisible from main. FR-0038 collision: two branches each wrote a file with that name. Attended session must merge/rebase; URGENT in INBOX.
- **Atlas frozen-loop escalation live** — strategy-readiness CLI deployed 2026-04-25T19:27Z; frozen-loop streak=3 means next `cycle.completed` event fires `cycle.escalated` URGENT. Expect URGENT-atlas-frozen-loop at next cycle unless a primitive is promoted.
- **Command login auth noise — non-issue** — 57 fail/success pairs within 15ms median are autofill races, not double-submissions. Do not re-file login URGENTs. Option A (meta-scan autofill_race filter) available if telemetry noise matters.

---

Archive for closed items: `system/active-issues-archive.md` (not auto-loaded).
