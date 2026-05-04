---
name: Active issues
description: Currently-live pressure on the workspace. Each entry is ≤3 lines. Historical / closed items live in `active-issues-archive.md`. Read this; load the archive on demand only.
updated: 2026-05-04
---

# Active issues

## Currently live

- **Atlas orphaned TESTING loop (P1)** — 7 hypotheses stuck in TESTING with no re-evaluation path after A+C+D2 deployed (2026-05-02). Atlas session restarted runner; P1 implementation (recurring TESTING re-evaluation each cycle) pending principal authorization. Route: `runtime/.handoff/atlas-p1-orphaned-testing-pending-auth-2026-05-04T02-49Z.md`.
- **reflect.sh Write bypass — cycle 10+** — reflect.sh `--disallowedTools` missing `Write` and several `Bash(*)` variants; reflection sessions can and do mutate project repos. Fix in `scripts/lib/reflect.sh` (Tier-C: requires attended operator session). FR-0040. INBOX: `reflect-sh-disallow-list-gap-2026-05-01T16-48Z.md`.
- **Proposal queue dead — saturation exception active** — 30+ synthesis proposals in INBOX, 0 dispatched in 15+ synthesis cycles. URGENT `URGENT-inbox-proposal-saturation-2026-04-28T08-50Z.md` is the meta-escalation; per saturation exception, further per-proposal URGENTs suppressed. Principal disposition needed: bulk-archive, Tier-B-auto authority, or explicit won't-fix.
- **Context-repo tick 401 failures** — unattended ticks for context-repository have been 401-failing since 2026-05-01T00:38Z. Reflection loop unaffected. Diagnosed and routed to context-repo session: `runtime/.handoff/context-repository-auth-failure-diagnosis-2026-05-04T02-49Z.md`.
- **LATEST_SYNTHESIS symlink repair** — server-maintenance flagged p2 (2026-05-04T01:25Z): synthesize.sh output size gate missing; symlink may point to corrupt/empty artifact. Tier-C fix in `scripts/lib/synthesize.sh`; requires attended operator session.
- **Command browser-layer verification** — server-side smoke is strong, but real-browser coverage remains a machine-owned gap. Old principal FR-0015 escalation archived; replacement handoff is `runtime/.handoff/command-browser-verification-owned-2026-04-25T1310Z.md`.
- **Synaplex site V1 deploy to synaplex.ai** — site scaffold builds clean at `projects/synaplex/site/dist/`; rebrand landed; deploy still pending. IA reshape decision open (§Open design questions in ADR-0027). Dispatched to synaplex session.
- **Synaplex loop L2/L3/L4 subsystems** — L1 intake live; Layer 2 reasoning, Layer 3 validation, Layer 4 presentation follow ADR-0029's bootstrap throttle (≤5 candidates/beat/day for 4 weeks).
- **Skillfoundry agentic inbound deploy** — Preflight landing route + `sourceType` + watcher restart; Launchpad Lint + LCI landing + telemetry; ≥1 blog post/probe/week. In flight per the skillfoundry session.
- **Discovery adapter post-fix findings** — 3 findings from Codex review on `2f63ae5`: `parse_assumption` 3-claim collapse, migrate.py swallows decision-header parse failures, parse-one-file boundary leaking. Finding B shipped; A and C pending.
- **Canon schema — polarity surface underspecified** — holistic audit (polarity vocabulary + coupled audit/citation/phase-0 surfaces + canon-CI gap FR-0035) dispatched to context-repo session.
- **Context-repo pass-2 retrofit** — M1+M2 retrofit for atlas landed (`49c24df`; 107/107 tests). skillfoundry-valuation-context retrofit proposal filed; awaiting skillfoundry session pickup.

## Pending principal (decisions only the principal can make)

- **Atlas P1 authorization** — principal must authorize or reject `_include_orphaned_testing` step in `run_cycle` (re-evaluate TESTING hypotheses each cycle that have a fresh dataset they haven't been tested on within `DATASET_RETEST_AFTER`). Atlas PM: "strict reading of A+C+D2 authorization wins; new step needs explicit auth."
- **Atlas 4h hypotheses decision** — 5 FORMULATED hypotheses stuck in off-universe timeframe. Options: re-add 4h to DEFAULT_UNIVERSE (they re-enter evaluation), or one-shot kill script (mark INFEASIBLE). Principal class: conflating "policy currently excludes" vs "claim cannot be tested."
- **Synaplex cap policy** — ADR-0029 §6 says "max 200 per source per day"; implementation does "max 200 per fetch" with union accumulation (HN reaching ~400/day). Options: A) truncate post-merge by score, B) by recency, C) ratify per-fetch semantic + amend ADR. Recommended: C. URGENT: `URGENT-synaplex-cap-policy-3rd-cycle-2026-05-01T14-42Z.md`.
- **LCI outreach channel** — 10 outreach drafts at `drafted` status since 2026-04-11 (23 days). Options: unblock (Tally form + outreach method), park explicitly (record in decisions/), or kill. URGENT: `URGENT-lci-outreach-blocked-22-days-2026-05-02.md`.

## Structural / background

- **Operator authority loop** — attached sessions can be executive/supervisor with repo write but no tmux/systemd host control. ADR-0015 amendment now forbids routing Evan to another "full admin" agent; repeated host-only needs must become an explicit operator bridge/tool.
- **Executive boundary discipline** — FR-0018 and follow-ons name the pattern where the executive session patches project code instead of shaping the PM layer. Ongoing; reinforced by ADR-0020 action-default + the people-or-money rubric memory.
- **ADR-0028 post-landing artifact hygiene** — artifact inbox still needs owned browser-layer proof before retiring the old `/_inbox` stopgap. Do not ask the principal for the proof path by default.
- **Workspace CLAUDE.md versioned as of `d09d2be`** — symlink from `/opt/workspace/CLAUDE.md` → `supervisor/workspace-claude.md`. All future workspace-charter edits land in git history via the supervisor repo.
- **Cowork is a secondary friction surface** — external commentary only; not a gate, validator, or backlog priority escalator. Phase D Cowork UI remains downstream of command Phase C and broader system backlog pressure. Durable contract: ADR-0032.

---

Archive for closed items: `system/active-issues-archive.md` (not auto-loaded).
