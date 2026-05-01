---
name: Active issues
description: Currently-live pressure on the workspace. Each entry is ≤3 lines. Historical / closed items live in `active-issues-archive.md`. Read this; load the archive on demand only.
updated: 2026-05-01
---

# Active issues

## Currently live

- **Atlas runner frozen 90h+ (CRITICAL)** — Signal-hash drift (12 formulated hypotheses unreachable) + BitMEX/Kraken data unavailable from Hetzner. Atlas PM recommends A+C+D2. Decision required from principal via `runtime/.handoff/atlas-pool-rotation-decision.md`. INBOX: `URGENT-atlas-pool-rotation-v2-two-blockers-2026-04-30T18-48Z.md`.
- **Headless tick 401 auth (CRITICAL, intermittent)** — Supervisor ticks at 10:47Z and 12:47Z on 2026-05-01 failed with 0 tool uses. Root cause: credential source divergence between reflection path and tick path. Operator action required (compare env vars, rotate key). INBOX: `URGENT-headless-tick-401-auth-2026-05-01T08-49Z.md`. FR-0039.
- **Synaplex cap policy — 3rd cycle** — ADR-0029 §6 says "200/source/day"; implementation does "200/fetch" producing ~400/day for HN. Recommendation is Option C (ratify per-fetch, amend §6). Amending ADR requires attended session (Tier-C). INBOX: `URGENT-synaplex-cap-policy-3rd-cycle-2026-05-01T14-42Z.md`.
- **Ghost-write pattern in tick sessions (9th window)** — Ticks emit write-success events for files that don't land on disk. Event model unreliable. Root cause undiagnosed. Fix: post-write `test -f` verification in tick wrapper (scripts/lib/, attended session required). FR-0038.
- **reflect.sh disallow-list gap** — Reflection sessions can write project files via `Write` tool and `Bash(python3)`. Also: an unidentified host process auto-commits CURRENT_STATE.md by scraping `git commit -m` commands embedded in the file. Fix in INBOX: `reflect-sh-disallow-list-gap-2026-05-01T16-48Z.md`. FR-0040.
- **Adversarial review non-functional workspace-wide** — `codex` not installed; EROFS in tick environments prevents installation. All unattended ticks fall back to same-model review or skip entirely. Atlas `_maybe_escalate_frozen_loop` has 7 bugs across 6 un-reviewed commits. Attended session must install codex or designate alternative.
- **INBOX proposal accumulation (36+ items, 0 landed in 9 cycles)** — Synthesis-to-execution pipeline stalled. All proposals require Tier-B/C authority (scripts/lib/, CLAUDE.md). Attended session must disposition: accept, defer, or close proposals in bulk. INBOX: `URGENT-inbox-proposal-saturation-2026-04-28T08-50Z.md`.
- **Command browser-layer verification** — Symphony-lite shipped (50/50 server-side smoke); browser-layer smoke not run. Machine-owned gap per `runtime/.handoff/command-browser-verification-owned-2026-04-25T1310Z.md`.
- **Synaplex site V1 deploy to synaplex.ai** — site scaffold builds clean at `projects/synaplex/site/dist/`; rebrand landed; deploy still pending. IA reshape decision open (§Open design questions in ADR-0027). Dispatched to synaplex session.
- **Synaplex loop L2/L3/L4 subsystems** — L1 intake live; Layer 2 reasoning (per-beat candidate emission), Layer 3 validation (counter-search + nightly integrity), Layer 4 presentation (writeups → site + newsletter) follow ADR-0029's bootstrap throttle (≤5 candidates/beat/day for 4 weeks).
- **Skillfoundry agentic inbound deploy** — Preflight landing route + `sourceType` + watcher restart; Launchpad Lint + LCI landing + telemetry; ≥1 blog post/probe/week. In flight per the skillfoundry session (scope now spans `/opt/workspace/projects/skillfoundry/` root).
- **Discovery adapter post-fix findings** — 3 new findings from Codex review on `2f63ae5`: `parse_assumption` 3-claim collapse, migrate.py swallows decision-header parse failures, parse-one-file boundary leaking. Triaged per handoff; Finding B ships this cycle, Finding A proposal drafts for spec-review, Finding C's ADR promotes to accepted-pending-scheduling.
- **Canon schema — polarity surface underspecified** — Codex review on `weakens_assumption` narrow proposal rejected narrow path. Holistic audit (reconcile polarity vocabulary + coupled audit/citation/phase-0 surfaces + canon-CI gap FR-0035) dispatched to context-repo session.
- **Context-repo pass-2 retrofit** — M1+M2 retrofit for atlas landed (`49c24df` in atlas repo; 107/107 tests). skillfoundry-valuation-context retrofit proposal filed; awaiting skillfoundry session pickup.

## Pending principal (people-or-money only)

- **Atlas pool-rotation decision** — binary choice (A+C+D2 recommended by atlas PM) to unblock runner frozen 90h. One-line response at `runtime/.handoff/atlas-pool-rotation-decision.md`. Not people-or-money, but strategically irreversible enough to require principal sign-off.
- **Synaplex scoring cron cadence** — currently runs 12×/day; 9 of 12 re-score unchanged corpus. When ANTHROPIC_API_KEY lands, ~9 wasted Sonnet calls/day. Decision needed before key arrives: reduce cron to match intake cadence (3×/day) or add dirty-check gate.

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
