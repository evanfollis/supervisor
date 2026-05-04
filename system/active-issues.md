---
name: Active issues
description: Currently-live pressure on the workspace. Each entry is ≤3 lines. Historical / closed items live in `active-issues-archive.md`. Read this; load the archive on demand only.
updated: 2026-05-04
---

# Active issues

## Critical — needs attended session or principal

- **Atlas runner frozen 42h+ (URGENT)** — runner producing `hypotheses_evaluated: 0` since A+C+D2 deploy (~May 1). 7 TESTING hypotheses orphaned; 5 FORMULATED permanently blocked. Fix requires: (1) `systemctl restart atlas-runner.service` to deploy 39b6d2f counter gate; (2) attended session to implement P1 (TESTING hypothesis inclusion) at `runner.py:1094–1110`. URGENT at `runtime/.handoff/URGENT-atlas-frozen-loop-2026-05-02T14-18-55Z.md`.
- **reflect.sh Write bypass (10+ cycles, URGENT)** — `--disallowedTools` blocks `Edit` and `NotebookEdit` but not `Write`. Reflection sessions have mutated project repos. One-line fix at `scripts/lib/reflect.sh:112` (Tier C — requires attended session with operator posture). URGENT at `runtime/.handoff/URGENT-reflect-sh-write-bypass-2026-05-03T15-23Z.md` and INBOX `reflect-sh-disallow-list-gap-2026-05-01T16-48Z.md`.
- **Ghost-write telemetry corruption** — tick sessions emit `session_reflected` events claiming file updates that did not occur (e.g., active-issues.md `updated: 2026-04-25` as of this tick; FR-0038 claimed written in 5+ ticks but doesn't exist). FR-0038 written this cycle. Root cause: tick sessions write events before verifying the write actually committed.
- **INBOX saturation — 43 items, 7-day SLA breached** — 39 synthesis proposals + 3 URGENTs in INBOX. Most proposals are Tier B/C (scripts/lib/, CLAUDE.md); only attended session can disposition. URGENT at `URGENT-inbox-proposal-saturation-2026-04-28T08-50Z.md`. Saturation exception active — no further per-proposal URGENTs until queue cleared.
- **LCI outreach blocked 22+ days (principal decision)** — 10 drafts at `drafted` since 2026-04-11; no external evidence for LCI assumption. Options: (A) unblock with channel decision, (B) park explicitly in decisions/, (C) kill track. URGENT at INBOX `URGENT-lci-outreach-blocked-22-days-2026-05-02.md`.
- **Synaplex cap policy — 3rd-cycle escalation (principal decision)** — ADR-0029 says "max 200 per source per day"; implementation does per-fetch. HN at ~400 items/day. Decision: (A) truncate by score, (B) truncate by recency, or (C) ratify per-fetch + amend ADR-0029. URGENT at INBOX `URGENT-synaplex-cap-policy-3rd-cycle-2026-05-01T14-42Z.md`.

## Currently live

- **Command browser-layer verification** — server-side smoke strong; real-browser coverage machine-owned gap. Handoff `runtime/.handoff/command-browser-verification-owned-2026-04-25T1310Z.md`.
- **Synaplex site V1 deploy to synaplex.ai** — scaffold builds clean at `projects/synaplex/site/dist/`; rebrand landed; deploy pending. IA reshape decision open (ADR-0027). Dispatched to synaplex session.
- **Synaplex loop L2/L3/L4 subsystems** — L1 intake live. L2 reasoning, L3 validation, L4 presentation follow ADR-0029 bootstrap throttle (≤5 candidates/beat/day for 4 weeks).
- **Synaplex score cron cadence** — 12 score runs/day re-score unchanged corpus; only 3 intake runs/day produce new data. Needs cron cadence fix before ANTHROPIC_API_KEY lands (Sonnet scoring ~9 wasted calls/day). Decision shares same gate as cap policy.
- **Skillfoundry agentic inbound deploy** — preflight landing + sourceType + watcher restart; Launchpad Lint + LCI landing + telemetry; ≥1 blog post/probe/week. In flight per skillfoundry session.
- **Discovery adapter post-fix findings** — 3 Codex review findings: `parse_assumption` 3-claim collapse, migrate.py swallows decision-header parse failures, parse-one-file boundary leaking. Triaged; Finding B ships this cycle, Finding A in spec-review.
- **Canon schema — polarity surface underspecified** — holistic audit (polarity vocabulary + audit/citation/phase-0 + FR-0035) dispatched to context-repo session.
- **Context-repo pass-2 retrofit** — M1+M2 retrofit for atlas landed. skillfoundry-valuation-context retrofit awaiting sf session pickup.
- **Doctor: 11 aged tick branches (>24h)** — branches `ticks/2026-05-02-14` through `ticks/2026-05-03-10` need attended merge. Playbook proposal at INBOX `proposal-merge-tick-branches-playbook-2026-04-26T03-37-07Z.md`.

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
