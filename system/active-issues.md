---
name: Active issues
description: Currently-live pressure on the workspace. Each entry is ≤3 lines. Historical / closed items live in `active-issues-archive.md`. Read this; load the archive on demand only.
updated: 2026-05-01
---

# Active issues

## Currently live

- **Command browser-layer verification** ~~RESOLVED~~ — 13/13 browser smoke checks pass (`0afbf4c`; screenshots at `runtime/browser-smoke/2026-05-01T05-51-12/`). Adversarial review complete. Symphony-lite handoff still pending; next command tick target.
- **Synaplex site V1 deploy to synaplex.ai** — site scaffold builds clean at `projects/synaplex/site/dist/`; rebrand landed; deploy still pending. IA reshape decision open (§Open design questions in ADR-0027). Dispatched to synaplex session.
- **Synaplex loop L2/L3/L4 subsystems** — L1 intake live; Layer 2 reasoning (per-beat candidate emission), Layer 3 validation (counter-search + nightly integrity), Layer 4 presentation (writeups → site + newsletter) follow ADR-0029's bootstrap throttle (≤5 candidates/beat/day for 4 weeks).
- **Skillfoundry agentic inbound deploy** — Preflight landing route + `sourceType` + watcher restart; Launchpad Lint + LCI landing + telemetry; ≥1 blog post/probe/week. In flight per the skillfoundry session (scope now spans `/opt/workspace/projects/skillfoundry/` root).
- **Discovery adapter post-fix findings** — 3 new findings from Codex review on `2f63ae5`: `parse_assumption` 3-claim collapse, migrate.py swallows decision-header parse failures, parse-one-file boundary leaking. Triaged per handoff; Finding B ships this cycle, Finding A proposal drafts for spec-review, Finding C's ADR promotes to accepted-pending-scheduling.
- **Canon schema — polarity surface underspecified** — Codex review on `weakens_assumption` narrow proposal rejected narrow path. Holistic audit (reconcile polarity vocabulary + coupled audit/citation/phase-0 surfaces + canon-CI gap FR-0035) dispatched to context-repo session.
- **Context-repo pass-2 retrofit** — M1+M2 retrofit for atlas landed (`49c24df` in atlas repo; 107/107 tests). skillfoundry-valuation-context retrofit proposal filed; awaiting skillfoundry session pickup.

## Pending principal (people-or-money only)

- **Atlas pool rotation decision overdue ~37h** — runner frozen since Apr 30 00:45Z. Two independent blockers (BitMEX/Kraken data unavailable; signal-hash drift on 12 formulated hypotheses). Atlas PM recommends A+C+D2. Reply via `runtime/.handoff/atlas-pool-rotation-decision.md`. See `INBOX/URGENT-atlas-pool-rotation-v2-two-blockers-2026-04-30T18-48Z.md`.
- **Synaplex L1 cap policy** — ADR-0029 §6 ambiguity (per-source vs per-fetch limit). Synaplex recommends Option C (ratify per-fetch semantic, amend ADR wording, no code change). See `INBOX/synaplex-cap-policy-decision-2026-04-30T14-49Z.md`.
- **INBOX saturation: 30+ proposals, 0 landed in 9 cycles** — attended session must disposition the backlog (execute, defer, or bulk close). `INBOX/URGENT-inbox-proposal-saturation-2026-04-28T08-50Z.md` is the entry point. Highest-leverage actions: iterate-patch-freeze CLAUDE.md rule, synthesis-translator dedup gate, merge-tick-branches playbook.

## Structural / background

- **401 auth blocking all project ticks** — tick sessions fail with `401 Invalid authentication credentials`; reflection jobs succeed. Credential path differs between tick and reflection launch paths. Every project tick is blocked until fixed. Server maintenance handoff at `runtime/.handoff/general-server-maintenance-2026-05-01T01-26-04Z.md`. Operator-level fix (credential rotation or env config). FR-0039.
- **Ghost-write pattern confirmed (FR-0038)** — tick events claim files are written that do not exist (FR-0038/0039 claimed in Apr-30 tick events; `ls friction/` ends at FR-0037). Extended to project tick wrappers: claimed URGENT files for auth failures don't exist in INBOX. Event log no longer reliable as truth source; primary verification required.
- **Doctor: FAIL — tick branch accumulation** — 19 branches aged >72h, 23 more >24h. Merge-tick-branches playbook proposed Apr 26 (9 cycles, 0 action). Requires attended session.
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
