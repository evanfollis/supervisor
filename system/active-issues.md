---
name: Active issues
description: Currently-live pressure on the workspace. Each entry is ≤3 lines. Historical / closed items live in `active-issues-archive.md`. Read this; load the archive on demand only.
updated: 2026-05-03
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
- **Atlas P1 — TESTING hypothesis re-evaluation** — Runner restarted (2026-05-02, PID 3359992, commit `c585891`). P1 fix (add TESTING hypothesis inclusion path in `runner.py:1094–1110`) awaits principal authorization. S3-P2 counter gate re-armed. `runtime/.handoff/general-atlas-orphaned-testing-failure-mode-2026-05-02T14-26Z.md`.
- **reflect.sh Write-tool bypass** — `--disallowedTools` blocks `Edit` and `NotebookEdit` but not `Write`. Reflection sessions have mutated project repos in cycles 9+ (cycle confirmed 2026-05-02). One-line fix at `scripts/lib/reflect.sh` line 112. Tier-C — requires attended operator session. URGENT in `runtime/.handoff/URGENT-reflect-sh-write-bypass-2026-05-03T15-23Z.md` and INBOX `reflect-sh-disallow-list-gap-2026-05-01T16-48Z.md`.
- **INBOX proposal saturation** — 39 proposals (oldest from 2026-04-25, 8 days) with 0 dispositions across 14 synthesis cycles. Saturation exception active. Mass attended-session disposition needed; URGENT in INBOX `URGENT-inbox-proposal-saturation-2026-04-28T08-50Z.md`.
- **Tick branch accumulation** — 12 aged tick branches from 2026-05-02 (24–47h) need merge. Doctor FAIL ongoing. Attended merge session required.

## Pending principal (people-or-money only)

- **LCI outreach channel decision** — 10 outreach drafts stalled 25 days (since 2026-04-11). Requires: Tally form setup, outreach channel selection, or explicit park/kill decision. URGENT in INBOX `URGENT-lci-outreach-blocked-22-days-2026-05-02.md`.
- **Synaplex cap policy (ADR-0029 §6)** — ADR says "max 200 per source per day"; implementation does "max 200 per fetch" (HN hitting ~277/day). Three options: truncate by score, truncate by recency, or ratify per-fetch semantic and amend ADR. Also: score cron fires 12×/day but intake only 3×/day — 9 wasted re-scores. Needs decision before ANTHROPIC_API_KEY lands. URGENT in INBOX `URGENT-synaplex-cap-policy-3rd-cycle-2026-05-01T14-42Z.md`.
- **Atlas P1 authorization** — implementing TESTING hypothesis re-evaluation path (`runner.py:1094–1110`). Without it the runner loop stays effectively frozen. (Listed above under live issues; surfaced here as the blocking principal decision.)

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
