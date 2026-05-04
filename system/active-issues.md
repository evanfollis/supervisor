---
name: Active issues
description: Currently-live pressure on the workspace. Each entry is ≤3 lines. Historical / closed items live in `active-issues-archive.md`. Read this; load the archive on demand only.
updated: 2026-05-04
---

# Active issues

## Critical / blocking

- **Atlas runner frozen P1** — `hypotheses_evaluated: 0` since A+C+D2 deploy (~May 1). Counter-gate fix `39b6d2f` pushed but not deployed. `sudo systemctl restart atlas-runner.service` needed (operator/principal). 7 orphaned TESTING hypotheses require attended-session fix at `runner.py:1094–1110`. URGENT: `runtime/.handoff/URGENT-atlas-frozen-loop-2026-05-02T14-18-55Z.md`.
- **reflect.sh Write bypass** — Line 112 blocks `Edit`/`NotebookEdit` but not `Write`. Reflections can mutate project repos. Cycle 10 open; URGENT: `runtime/.handoff/URGENT-reflect-sh-write-bypass-2026-05-03T15-23Z.md`. Fix: add `"Write"` to disallowedTools at `scripts/lib/reflect.sh:112`. Tier C — operator needed.
- **Supervisor reflection mutated HEAD** — `reflect.sh` safety net did not catch a HEAD advance in supervisor at 2026-05-03T14Z. Investigate how model bypassed blocklist. URGENT: `runtime/.handoff/URGENT-supervisor-reflection-mutated-head.md`.
- **Tick branch merge backlog** — 21 tick branches >24h (oldest 69h). All governance writes on tick branches are ephemeral until merged. Attended merge session needed.

## Currently live

- **Command browser-layer verification** — server-side smoke is strong, but real-browser coverage remains a machine-owned gap. Old principal FR-0015 escalation archived; replacement handoff is `runtime/.handoff/command-browser-verification-owned-2026-04-25T1310Z.md`.
- **Synaplex site V1 deploy to synaplex.ai** — site scaffold builds clean at `projects/synaplex/site/dist/`; rebrand landed; deploy still pending. IA reshape decision open (§Open design questions in ADR-0027). Dispatched to synaplex session.
- **Synaplex loop L2/L3/L4 subsystems** — L1 intake live; Layer 2 reasoning (per-beat candidate emission), Layer 3 validation (counter-search + nightly integrity), Layer 4 presentation (writeups → site + newsletter) follow ADR-0029's bootstrap throttle (≤5 candidates/beat/day for 4 weeks).
- **Synaplex cap policy** — ADR-0029 §6 says "max 200/source/day"; implementation does "max 200/fetch" (union accumulates to ~400 for HN). Decision needed: truncate post-merge by score/recency, or ratify per-fetch semantic + amend ADR. URGENT in INBOX: `URGENT-synaplex-cap-policy-3rd-cycle-2026-05-01T14-42Z.md`.
- **Skillfoundry agentic inbound deploy** — Preflight landing route + `sourceType` + watcher restart; Launchpad Lint + LCI landing + telemetry; ≥1 blog post/probe/week. In flight per the skillfoundry session. Test telemetry isolation conftest shipped (`8fcf2d1`, 61/61 pass).
- **LCI outreach blocked** — 10 outreach drafts at `drafted` since 2026-04-11 (23+ days). Channel decision required: Tally form, outreach method, or explicit park/kill. URGENT in INBOX: `URGENT-lci-outreach-blocked-22-days-2026-05-02.md`.
- **Discovery adapter post-fix findings** — 3 new findings from Codex review on `2f63ae5`: `parse_assumption` 3-claim collapse, migrate.py swallows decision-header parse failures, parse-one-file boundary leaking. Triaged per handoff; Finding B ships this cycle, Finding A proposal drafts for spec-review, Finding C's ADR promotes to accepted-pending-scheduling.
- **Canon schema — polarity surface underspecified** — Codex review on `weakens_assumption` narrow proposal rejected narrow path. Holistic audit (reconcile polarity vocabulary + coupled audit/citation/phase-0 surfaces + canon-CI gap FR-0035) dispatched to context-repo session.
- **Context-repo pass-2 retrofit** — M1+M2 retrofit for atlas landed (`49c24df` in atlas repo; 107/107 tests). skillfoundry-valuation-context retrofit proposal filed; awaiting skillfoundry session pickup.
- **INBOX proposal queue** — 39+ items, 0 proposals landed in 16 cycles. Root cause: all Tier B/C changes require attended operator session. Structural unblock is Tier-B-auto authority decision (INBOX: `proposal-tier-b-auto-authority-2026-05-02T18-50Z.md`).
- **Telemetry truth source degradation** — Two classes of false signal in `events.jsonl`: (1) tick ghost-writes claim changes on main that only exist on branches; (2) test pollution — 2 `sourceType:user` events from pytest runs in stream. SF-harness conftest fixes (2) for future runs; historical entries remain. Tick branch field (Proposal 1) would fix (1).
- **LATEST_SYNTHESIS pointer corrupted** — symlink at `runtime/.meta/LATEST_SYNTHESIS` writes through to Apr 29 artifact, destroying historical content. Fix in `scripts/lib/synthesize.sh` (Tier C). Proposal 4 in INBOX.
- **Rotation-blind reflection telemetry** — 02:xx UTC reflection cycles miss ~10h of events due to midnight log rotation. Fix: include gzipped prior-day archive in query. Proposal 3 in INBOX.

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

---

Archive for closed items: `system/active-issues-archive.md` (not auto-loaded).
