---
name: Active issues
description: Currently-live pressure on the workspace. Each entry is ≤3 lines. Historical / closed items live in `active-issues-archive.md`. Read this; load the archive on demand only.
updated: 2026-04-28
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

## Governance substrate (active blockers — requires attended session)

- **INBOX saturation — dispatch obligation violated** — 19 items in INBOX (17 proposals + URGENT-inbox-saturation + adr-review-complete-0031-0032); all require attended session action; oldest items 77h old. Saturation URGENT filed 2026-04-28T08:50Z; iterate-patch-freeze duplicate proposals added 2026-04-28T15:34Z. Attended session must disposition or bulk-close.
- **Doctor FAIL: 2 tick branches >72h** — `ticks/2026-04-25-16` (75h) and `ticks/2026-04-25-18` (73h) exceed the 72h FAIL threshold; 21 additional branches >24h. Attended merge or branch cleanup needed.
- **.reviews/ EROFS** — confirmed in both worktree and non-worktree tick sessions. ADR-0031/ADR-0032 review artifacts are in `handoffs/INBOX/adr-review-complete-0031-0032-2026-04-28T02-49Z.md`; cannot be moved to `.reviews/` until EROFS constraint is understood/resolved.
- **CLAUDE.md amendment pending** — 2 duplicate iterate-patch-freeze proposals in INBOX (`proposal-iterate-patch-freeze-2026-04-28T15-34-37Z.md`, `proposal-iteratively-patched-functions-freeze-review-2026-04-28T15-35-41Z.md`); same text, high priority from synthesis; attended session should de-duplicate and accept/reject.
- **Synthesis output gate unimplemented** — `proposal-synthesis-output-gate-2026-04-28T03-30-01Z.md` in INBOX 36h; the gate prevents 67-byte stub synthesis files. Currently synthesis is 17KB (OK), but fix is needed to prevent recurrence.

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
