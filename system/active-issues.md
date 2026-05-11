---
name: Active issues
description: Currently-live pressure on the workspace. Each entry is ≤3 lines. Historical / closed items live in `active-issues-archive.md`. Read this; load the archive on demand only.
updated: 2026-05-11
---

# Active issues

## CRITICAL (blocks autonomous repair)

- **reflect.sh Write bypass — confirmed exploit, ~18 exposure windows** — `scripts/lib/reflect.sh:112` blocks `Edit` and `NotebookEdit` but not `Write`. Confirmed exploitation on May 2 and May 6; reflection sessions can mutate any project repo. Fix is 1 line: add `"Write"` to `--disallowedTools`. Requires attended session with Tier-B/C access. URGENT in INBOX since May 1 (`URGENT-reflect-sh-disallow-gap-aged-2026-05-06T02-47Z.md`, 133h old). Cycle-20 Proposal #1; cycle-30 confirms still open.
- **Ghost-write cascade — now at governance tier with false self-verification** — Tick branches claim Tier-A writes that don't land on main. Escalated: ticks now emit false self-verification ("FR-0040 written first time") while the file doesn't exist. FR-0040 filed on main this tick (first real landing, 2026-05-11T16:47Z). ADR-0033 still absent from decisions/ despite 6+ `decision_recorded` events. Requires Tier-B-auto authority decision or attended merge playbook. Cycle-29/30 Proposal 1 (disk verification gate) is the near-term fix.
- **Synthesis dispatch obligation — 30 cycles, 8/35 proposals resolved (23%)** — Cycle-30 deadline 2026-05-12T03:25Z. All 3 new proposals require Tier-C access (scripts/lib/ edits). INBOX: `cycle29-synthesis-dispatch-2026-05-11T08-48Z.md`. Empirically validated: dispatch is the binding constraint — synaplex dual-emit resolved in same session it was dispatched (d0220a9).

## Currently live

- **Command browser-layer verification** — server-side smoke is strong, but real-browser coverage remains a machine-owned gap. Old principal FR-0015 escalation archived; replacement handoff is `runtime/.handoff/command-browser-verification-owned-2026-04-25T1310Z.md`.
- **Command symphonyStore.ts:132 sourceType hardcoded** — 6-cycle escalation; URGENT filed 2026-05-11T16:47Z; handoff dispatched to command session. 3-line fix, no ADR. Track until command session confirms deployed.
- **Synaplex site V1 deploy to synaplex.ai** — site scaffold builds clean at `projects/synaplex/site/dist/`; rebrand landed; deploy still pending. IA reshape decision open (§Open design questions in ADR-0027). Dispatched to synaplex session.
- **Synaplex dual-emit RESOLVED** — RSS/HN/arxiv duplicate-emit bug fixed (d0220a9, 2026-05-11). 9+ cycle carry-forward closed. Proves dispatch-not-diagnosis is binding constraint.
- **Synaplex loop L2/L3/L4 subsystems** — L1 intake live; Layer 2 reasoning (per-beat candidate emission), Layer 3 validation (counter-search + nightly integrity), Layer 4 presentation (writeups → site + newsletter) follow ADR-0029's bootstrap throttle (≤5 candidates/beat/day for 4 weeks).
- **Synaplex cap policy doc/code divergence** — ADR-0029 says "max 200/source/day"; implementation does "max 200/fetch with union accumulation" (HN reaches 277+/day). Dispatched to synaplex session this tick. INBOX URGENT archived.
- **Skillfoundry agentic inbound deploy** — Preflight landing route + `sourceType` + watcher restart; Launchpad Lint + LCI landing + telemetry; ≥1 blog post/probe/week. In flight per the skillfoundry session (scope now spans `/opt/workspace/projects/skillfoundry/` root).
- **LCI outreach blocked** — 10 outreach drafts at `drafted` since 2026-04-11 (30+ days). Channel decision required from principal (Tally form, outreach method, or explicit park/kill). INBOX: `URGENT-aged-lci-outreach-blocked-2026-05-09T02-49Z.md` (61h old).
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
