---
name: Active issues
description: Currently-live pressure on the workspace. Each entry is ≤3 lines. Historical / closed items live in `active-issues-archive.md`. Read this; load the archive on demand only.
updated: 2026-05-07
---

# Active issues

## CRITICAL (blocks autonomous repair)

- **reflect.sh Write bypass — confirmed exploit, 8+ exposure windows** — `scripts/lib/reflect.sh:112` blocks `Edit` and `NotebookEdit` but not `Write`. Confirmed exploitation on May 2 and May 6; reflection sessions can mutate any project repo. Fix is 1 line: add `"Write"` to `--disallowedTools`. Requires attended session with Tier-B/C access. URGENT in INBOX since May 1 (`URGENT-reflect-sh-disallow-gap-aged-2026-05-06T02-47Z.md`). Cycle-20 Proposal #1.
- **Ghost-write cascade — tick writes never reach main** — All tick-session Tier-A writes (active-issues, friction records, events) land on `ticks/<iso>` branches, not main. Tick wrapper commits to tick branch after session exits. `friction/` ceiling on main: FR-0037 (all FR-0038+ only on tick branches). active-issues.md on main stale ~6 weeks. Requires Tier-B-auto authority decision or attended merge playbook. INBOX: `URGENT-inbox-proposal-saturation` (Apr 28, 9 days). Synthesis Proposal #18 is the structural unblock.
- **Synthesis dispatch obligation — cycle-20 deadline passed** — Cycle-20 synthesis fired 2026-05-06T03:25Z; 24h dispatch deadline (08:52Z May 7) passed without project handoffs. All 25 unlanded proposals require Tier-C access. INBOX URGENT filed this tick. Cycle-21 synthesis fires ~03:25Z May 7. Score: 1/26 proposals landed across 20 cycles.

## Currently live

- **Command browser-layer verification** — server-side smoke is strong, but real-browser coverage remains a machine-owned gap. Old principal FR-0015 escalation archived; replacement handoff is `runtime/.handoff/command-browser-verification-owned-2026-04-25T1310Z.md`.
- **Synaplex site V1 deploy to synaplex.ai** — site scaffold builds clean at `projects/synaplex/site/dist/`; rebrand landed; deploy still pending. IA reshape decision open (§Open design questions in ADR-0027). Dispatched to synaplex session.
- **Synaplex loop L2/L3/L4 subsystems** — L1 intake live; Layer 2 reasoning (per-beat candidate emission), Layer 3 validation (counter-search + nightly integrity), Layer 4 presentation (writeups → site + newsletter) follow ADR-0029's bootstrap throttle (≤5 candidates/beat/day for 4 weeks).
- **Synaplex cap policy doc/code divergence** — ADR-0029 says "max 200/source/day"; implementation does "max 200/fetch with union accumulation" (HN reaches 277+/day). Dispatched to synaplex session this tick. INBOX URGENT archived.
- **Skillfoundry agentic inbound deploy** — Preflight landing route + `sourceType` + watcher restart; Launchpad Lint + LCI landing + telemetry; ≥1 blog post/probe/week. In flight per the skillfoundry session (scope now spans `/opt/workspace/projects/skillfoundry/` root).
- **LCI outreach blocked** — 10 outreach drafts at `drafted` since 2026-04-11 (26 days). Channel decision required from principal (Tally form, outreach method, or explicit park/kill). INBOX: `URGENT-lci-outreach-blocked-22-days-2026-05-02.md`.
- **Discovery adapter post-fix findings** — 3 new findings from Codex review on `2f63ae5`: `parse_assumption` 3-claim collapse, migrate.py swallows decision-header parse failures, parse-one-file boundary leaking. Triaged per handoff; Finding B ships this cycle, Finding A proposal drafts for spec-review, Finding C's ADR promotes to accepted-pending-scheduling.
- **Canon schema — polarity surface underspecified** — Codex review on `weakens_assumption` narrow proposal rejected narrow path. Holistic audit (reconcile polarity vocabulary + coupled audit/citation/phase-0 surfaces + canon-CI gap FR-0035) dispatched to context-repo session.
- **Context-repo pass-2 retrofit** — M1+M2 retrofit for atlas landed (`49c24df` in atlas repo; 107/107 tests). skillfoundry-valuation-context retrofit proposal filed; awaiting skillfoundry session pickup.
- **Server maintenance p2** — kernel reboot required (6.8.0-111 installed, 6.8.0-110 running); workspace-synthesize.service failed 2026-05-06T15:27Z. INBOX: `server-maintenance-p2-items-2026-05-07T02-48Z.md`. Operator action needed.

## Pending principal (people-or-money only)

- **LCI channel decision** — park, kill, or unblock the 26-day stalled outreach track. See `URGENT-lci-outreach-blocked` in INBOX.
- **Tier-B-auto authority** — grant or deny ticks authority to implement additive `scripts/lib/` changes without attended gating. Structural unblock for ~10 standing synthesis proposals. 8-cycle carry-forward (cycle-20 Q1). Without it, workspace remains diagnosis-complete and action-incomplete.

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
