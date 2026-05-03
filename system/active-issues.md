---
name: Active issues
description: Currently-live pressure on the workspace. Each entry is ≤3 lines. Historical / closed items live in `active-issues-archive.md`. Read this; load the archive on demand only.
updated: 2026-05-03
---

# Active issues

## Currently live

- **Atlas runner frozen 46h+** — P1 (commit 71224e9) + S3-P2 gate both in main since ~17:05Z May 2. Service last restarted May 2 before P1 landed; 14 consecutive cycles show `hypotheses_evaluated: 0`. 24h dispatch obligation breached. Fix: `sudo systemctl restart atlas-runner.service` (principal-blocked, Tier-C).
- **INBOX proposal queue saturation (35+ items, 0/19 landed)** — 14 synthesis cycles; 0% proposal execution via the INBOX/proposal-* path. URGENT-inbox-proposal-saturation 5+ days old. Synthesis confirms URGENT handoff path works; proposal path is structural dead letter box. Tier-B-auto authority decision would unblock.
- **Tick branch merge backlog** — 21 aged branches (>24h); doctor FAIL ongoing. Playbook proposal in INBOX. Merge requires operator access (git merge + push on main, or `workspace.sh` merge helper). Principal-blocked or operator session needed.
- **reflect.sh Write bypass** — Cycle 9+; `Write` not in `--disallowedTools` so reflection sessions can mutate project files undetected (safety net only catches committed HEAD changes). Synthesis wrote URGENT to `runtime/.handoff/URGENT-reflect-sh-write-bypass-2026-05-03T15-23Z.md`. Fix in Tier-C `scripts/lib/reflect.sh`.
- **Test telemetry sink pollution** — sf-harness migrate.py tests (531946f) emitted 2 events with `sourceType: user` and pytest tmp path into production `events.jsonl`. S1-P2 violation confirmed; timestamps 1777775272667, 1777775280921. Conftest isolation fixture needed.
- **Command browser-layer verification** — server-side smoke strong; real-browser coverage gap. Handoff: `runtime/.handoff/command-browser-verification-owned-2026-04-25T1310Z.md`.
- **Synaplex site V1 deploy to synaplex.ai** — scaffold builds clean at `projects/synaplex/site/dist/`; deploy pending. IA reshape decision open (ADR-0027). Dispatched to synaplex session.
- **Synaplex loop L2/L3/L4 subsystems** — L1 intake live; L2/L3/L4 follow ADR-0029 bootstrap throttle (≤5 candidates/beat/day for 4 weeks).
- **Skillfoundry agentic inbound deploy** — Preflight + `sourceType` + watcher restart; Launchpad Lint + LCI landing + telemetry; ≥1 blog post/probe/week. In flight per skillfoundry session.
- **Discovery adapter post-fix findings** — 3 findings from Codex review `2f63ae5`: `parse_assumption` 3-claim collapse, migrate.py parse-failure swallow, parse-one-file boundary leak. Finding B shipped; A and C pending context-repo session.
- **Canon schema — polarity surface underspecified** — holistic audit (vocabulary + coupled surfaces + FR-0035 canon-CI gap) dispatched to context-repo session.
- **Context-repo pass-2 retrofit** — M1+M2 for atlas landed (`49c24df`, 107/107 tests); skillfoundry-valuation retrofit pending skillfoundry session pickup.

## Pending principal (one-command or one-decision items)

- **Atlas runner restart** — `sudo systemctl restart atlas-runner.service` deploys P1 + S3-P2 gate. 46h+ frozen. 24h dispatch obligation breached. One command.
- **Synaplex cap policy** — ADR-0029 says "200/source/day"; impl does "200/fetch" with union. HN at 277 items. Decide: (A) truncate by score, (B) truncate by recency, (C) ratify per-fetch semantic + amend ADR-0029. URGENT 3rd cycle in INBOX.
- **LCI outreach decision** — 10 drafts at `drafted` since 2026-04-11 (22+ days). Channel choice (Tally form + method) OR explicit park/kill decision. URGENT 3rd cycle in INBOX.
- **Tier-B-auto authority** — approving autonomous execution for additive, 2+-cycle, infrastructure-only proposal changes would unblock reflect.sh fix + 14 stale INBOX proposals. Alternative: 30-min attended INBOX triage. Without one of these, synthesis proposals cannot be consumed.

## Structural / background

- **Operator authority loop** — attached sessions have repo write but no tmux/systemd host control. ADR-0015 amendment forbids routing Evan to another "full admin" agent; repeated host-only needs must become an explicit operator bridge/tool.
- **Executive boundary discipline** — FR-0018 and follow-ons. Ongoing; reinforced by ADR-0020 action-default + people-or-money rubric.
- **ADR-0028 post-landing artifact hygiene** — needs browser-layer proof before retiring `/_inbox` stopgap.
- **Workspace CLAUDE.md versioned as of `d09d2be`** — symlink `/opt/workspace/CLAUDE.md` → `supervisor/workspace-claude.md`. Autonomous-exec loop demonstrated.
- **Cowork is secondary friction surface** — not a gate or priority escalator. ADR-0032.

---

Archive for closed items: `system/active-issues-archive.md` (not auto-loaded).
