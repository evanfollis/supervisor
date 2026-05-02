---
name: Active issues
description: Currently-live pressure on the workspace. Each entry is ≤3 lines. Historical / closed items live in `active-issues-archive.md`. Read this; load the archive on demand only.
updated: 2026-05-02
---

# Active issues

## URGENT — requires attended session or principal

- **Ghost-write false verification (FR-0038)** — tick sessions produce explicit "verified on disk" claims that are empirically false. active-issues.md was `updated: 2026-04-25` through 7 consecutive ticks claiming to update it; FR-0038/0039/0040 claimed written in 04:47Z tick but absent until this session. Root cause undiagnosed; requires attended investigation of write path.
- **Headless project ticks failing — 401 auth (FR-0039)** — all headless project ticks return `401 Invalid authentication credentials` since 2026-04-30 late. Reflection jobs unaffected. Operator action: compare credential source for tick vs reflection path, rotate stale key, confirm with one manual tick run. INBOX: `URGENT-headless-tick-401-auth-2026-05-01T08-49Z.md`
- **Atlas S3-P2 fix undeployed** — commit `39b6d2f` (S3-P2 frozen-loop gate replacement, 156/156 tests pass) shipped 2026-05-02T02:11Z but service not restarted. Operator: `sudo systemctl restart atlas-runner.service`. Handoff: `runtime/.handoff/general-atlas-s3p2-restart-needed-2026-05-02T04-47Z.md`
- **LCI outreach blocked 22 days (principal decision)** — 10 outreach drafts at `drafted` status since 2026-04-11. Channel decision required: Tally form, outreach method, or explicit park/kill. 3-cycle escalation threshold crossed. INBOX: `URGENT-lci-outreach-blocked-22-days-2026-05-02.md`
- **Synaplex cap policy — 4th cycle (principal decision)** — ADR-0029 §6 says "max 200 per source per day"; implementation does "max 200 per fetch." Recommendation: Option C (amend ADR-0029 §6 wording). Score cron cadence also needs fix before API key lands. INBOX: `URGENT-synaplex-cap-policy-3rd-cycle-2026-05-01T14-42Z.md`
- **INBOX proposal saturation (40 items, 0 landed)** — 40 proposals in INBOX after 11 synthesis cycles. All target Tier-B/C surfaces that tick sessions cannot modify. Attended bulk triage needed to restore URGENT signal quality. INBOX: `URGENT-inbox-proposal-saturation-2026-04-28T08-50Z.md`; FR-0041.
- **reflect.sh Write bypass (FR-0040)** — `--disallowedTools` does not block `Write` or `Bash(python3:*)`. Reflections mutate project files. Policy contradiction: reflections declared read-only but Write CURRENT_STATE.md every cycle. Fix in `scripts/lib/reflect.sh` (Tier C, requires attended). INBOX: `reflect-sh-disallow-list-gap-2026-05-01T16-48Z.md`

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

- **Operator authority loop** — attached sessions can be executive/supervisor with repo write but no tmux/systemd host control. ADR-0015 amendment now forbids routing Evan to another "full admin" agent; repeated host-only needs must become an explicit operator bridge/tool.
- **Executive boundary discipline** — FR-0018 and follow-ons name the pattern where the executive session patches project code instead of shaping the PM layer. Ongoing; reinforced by ADR-0020 action-default + the people-or-money rubric memory.
- **ADR-0028 post-landing artifact hygiene** — artifact inbox still needs owned browser-layer proof before retiring the old `/_inbox` stopgap. Do not ask the principal for the proof path by default.
- **Workspace CLAUDE.md versioned as of `d09d2be`** — symlink from `/opt/workspace/CLAUDE.md` → `supervisor/workspace-claude.md`. All future workspace-charter edits land in git history via the supervisor repo. Autonomous-exec loop demonstrated for this change (synthesis → translator → INBOX handoff → executive commit).
- **Cowork is a secondary friction surface** — external commentary only; not a gate, validator, or backlog priority escalator. Phase D Cowork UI remains downstream of command Phase C and broader system backlog pressure. Durable contract: ADR-0032.
- **Doctor: FAIL** — 33 aged tick branches (10 over 72h threshold), 40 INBOX items violating SLA. Attended merge playbook execution needed.

---

Archive for closed items: `system/active-issues-archive.md` (not auto-loaded).
