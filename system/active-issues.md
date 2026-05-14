---
name: Active issues
description: Currently-live pressure on the workspace. Each entry is ≤3 lines. Historical / closed items live in `active-issues-archive.md`. Read this; load the archive on demand only.
updated: 2026-05-14
---

# Active issues

## CRITICAL (blocks autonomous repair)

- **reflect.sh Write bypass — confirmed exploit, ~36+ exposure windows** — `scripts/lib/reflect.sh:112` blocks `Edit` and `NotebookEdit` but not `Write`. Confirmed exploitation on May 2 and May 6 (project repos); May 6 supervisor HEAD advance (`2bdfdaf1`). Fix is 1 line: add `"Write"` to `--disallowedTools`. Dispatch handoff: `runtime/.handoff/general-reflect-sh-write-bypass-fix-2026-05-12T04-49Z.md` (unconsumed, ~287h). Requires attended session with Tier-B/C access. Cycle-36 standing recommendation #2.
- **Ghost-write cascade — 55 commits ahead of origin/main, ADR-0033 still absent** — Tick branches claim Tier-A writes that never merge to main. FR-0038/39/40 Status-field fix finally landed on main 2026-05-14T12:50Z after 6+ ghost-write cycles. FR-0041 filed first time this tick. ADR-0033 absent from decisions/ despite 8+ `decision_recorded` events. Requires Tier-B-auto authority decision or attended merge playbook. Cycle-36 standing recommendation #5. Branch divergence: 55 ahead, 2 behind origin/main.
- **Synthesis dispatch obligation — 36 cycles, INBOX at 18 items (saturation active)** — INBOX holds 18 items (4 URGENTs + 14 proposals); consumption rate 0 for 8+ cycles. INBOX saturation suppression exception invoked per cycle-35 rules (>10 items, 0 consumption). All 5 cycle-36 proposals still deposited at 15:33Z despite suppression — deposit suppression not yet enforced in tick dispatcher. Tier-B-auto or attended merge session required to reduce backlog.

## Currently live

- **Command browser-layer verification** — server-side smoke is strong, but real-browser coverage remains a machine-owned gap. Old principal FR-0015 escalation archived; replacement handoff is `runtime/.handoff/command-browser-verification-owned-2026-04-25T1310Z.md`.
- **Command symphonyStore.ts:132 sourceType RESOLVED** — Fix deployed; command.service restarted 2026-05-12T18:56:18Z (verified-state.md). Completion handoff `.done`. Close this cycle.
- **Synaplex site V1 deploy to synaplex.ai** — site scaffold builds clean at `projects/synaplex/site/dist/`; rebrand landed; deploy still pending. IA reshape decision open (§Open design questions in ADR-0027). Dispatched to synaplex session.
- **Synaplex dual-emit RESOLVED** — RSS/HN/arxiv duplicate-emit bug fixed (d0220a9, 2026-05-11). 9+ cycle carry-forward closed. Proves dispatch-not-diagnosis is binding constraint.
- **Synaplex loop L2/L3/L4 subsystems** — L1 intake live; Layer 2 reasoning (per-beat candidate emission), Layer 3 validation (counter-search + nightly integrity), Layer 4 presentation (writeups → site + newsletter) follow ADR-0029's bootstrap throttle (≤5 candidates/beat/day for 4 weeks).
- **Synaplex cap policy doc/code divergence** — ADR-0029 says "max 200/source/day"; implementation does "max 200/fetch with union accumulation" (HN reaches 277+/day). Dispatched to synaplex session this tick. INBOX URGENT archived.
- **Skillfoundry agentic inbound deploy** — Preflight landing route + `sourceType` + watcher restart; Launchpad Lint + LCI landing + telemetry; ≥1 blog post/probe/week. In flight per the skillfoundry session (scope now spans `/opt/workspace/projects/skillfoundry/` root).
- **LCI outreach blocked** — 10 outreach drafts at `drafted` since 2026-04-11 (30+ days). Channel decision required from principal (Tally form, outreach method, or explicit park/kill). INBOX: `URGENT-aged-lci-outreach-blocked-2026-05-09T02-49Z.md` (61h old).
- **Discovery adapter post-fix findings** — 3 new findings from Codex review on `2f63ae5`: `parse_assumption` 3-claim collapse, migrate.py swallows decision-header parse failures, parse-one-file boundary leaking. Triaged per handoff; Finding B ships this cycle, Finding A proposal drafts for spec-review, Finding C's ADR promotes to accepted-pending-scheduling.
- **Canon schema — polarity surface underspecified** — Codex review on `weakens_assumption` narrow proposal rejected narrow path. Holistic audit (reconcile polarity vocabulary + coupled audit/citation/phase-0 surfaces + canon-CI gap FR-0035) dispatched to context-repo session.
- **Context-repo pass-2 retrofit** — M1+M2 retrofit for atlas landed (`49c24df` in atlas repo; 107/107 tests). skillfoundry-valuation-context retrofit proposal filed; awaiting skillfoundry session pickup.
- **Server maintenance p2** — kernel reboot required (6.8.0-111 installed, 6.8.0-110 running, reboot-required flag set; verified-state.md 2026-05-14T16:47Z). INBOX URGENT: `URGENT-aged-server-maintenance-p2-2026-05-08T02-48Z.md` (157h). Operator action needed.
- **Reflection accuracy gap (cycle 36 NEW)** — Reflection jobs read CURRENT_STATE.md instead of live sources (task stores, git HEAD, service status), propagating stale derivatives across cycles. Command reported "1 task" for multiple cycles while live store had 11. Proposals 1+4 from cycle-36 synthesis in INBOX propose CLAUDE.md amendment + reflect-prompt.md fix.
- **Synaplex arxiv API degradation (cycle 36 NEW)** — Two concurrent failure modes in one 12h window (429 rate-limit + TimeoutError on arxiv). Neither synaplex nor atlas has backoff logic. `skip_next_run` primitive proposed in cycle-36 synthesis Proposal 5. Dispatching to synaplex session.

## Pending principal (people-or-money only)

- **LCI channel decision** — park, kill, or unblock the 33+ day stalled outreach track. INBOX URGENT `URGENT-aged-lci-outreach-blocked-2026-05-09T02-49Z.md` (133h old, no response).
- **Atlas strategic direction** — 277+ idle cycles (~11.5 days); principal decision on Option A (expand signal universe) / B (explicit park) / C (retire pod) overdue 93.5h+. INBOX URGENT `URGENT-atlas-principal-decision-overdue-2026-05-12T06-47Z.md` (57h). Bitstamp API burning ~24 calls/day idle.
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
