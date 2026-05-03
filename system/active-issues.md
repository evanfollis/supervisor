---
name: Active issues
description: Currently-live pressure on the workspace. Each entry is ≤3 lines. Historical / closed items live in `active-issues-archive.md`. Read this; load the archive on demand only.
updated: 2026-05-03
---

# Active issues

## Currently live

- **Atlas P1 undeployed — 24h dispatch obligation breached** — commit 71224e9 (S3-P2 counter gate + hypothesis evaluation fix) has been in `main` since ~17:05Z May 2, 46h+ unfrozen. Service last restarted before P1 landed; 14+ consecutive cycles with `hypotheses_evaluated: 0`. Requires `sudo systemctl restart atlas-runner.service`. URGENT at `runtime/.handoff/URGENT-atlas-frozen-loop-2026-05-02T14-18-55Z.md`.
- **reflect.sh Write bypass — propose-only contract violated** — `scripts/lib/reflect.sh` blocks `Edit` and `NotebookEdit` but not `Write`. Reflection sessions can write files silently past the safety net (dirty-tree check only catches HEAD advances). Supervisor reflection at 14:24Z May 3 advanced HEAD via autocommit path. Fix: add `"Write"` to `--disallowedTools` at line 112. URGENT at `runtime/.handoff/URGENT-reflect-sh-write-bypass-2026-05-03T15-23Z.md`. Tier-C — needs operator.
- **Test telemetry pollution in sf-harness** — commit 531946f (migrate.py) wrote two events with `sourceType: user` and `venture_root: /tmp/pytest-of-root/...` to the production telemetry sink. ADR-0019 + S1-P2 both violated. Fix: conftest autouse fixture redirecting `*_TELEMETRY_PATH` to a temp dir. Synthesis proposal 4.
- **Command browser-layer verification** — server-side smoke is strong, but real-browser coverage remains a machine-owned gap. Old principal FR-0015 escalation archived; replacement handoff is `runtime/.handoff/command-browser-verification-owned-2026-04-25T1310Z.md`.
- **Synaplex site V1 deploy to synaplex.ai** — site scaffold builds clean at `projects/synaplex/site/dist/`; rebrand landed; deploy still pending. IA reshape decision open (§Open design questions in ADR-0027). Dispatched to synaplex session.
- **Synaplex loop L2/L3/L4 subsystems** — L1 intake live; Layer 2 reasoning (per-beat candidate emission), Layer 3 validation (counter-search + nightly integrity), Layer 4 presentation (writeups → site + newsletter) follow ADR-0029's bootstrap throttle (≤5 candidates/beat/day for 4 weeks).
- **Skillfoundry agentic inbound deploy** — Preflight landing route + `sourceType` + watcher restart; Launchpad Lint + LCI landing + telemetry; ≥1 blog post/probe/week. In flight per the skillfoundry session (scope now spans `/opt/workspace/projects/skillfoundry/` root).
- **Discovery adapter post-fix findings** — 3 new findings from Codex review on `2f63ae5`: `parse_assumption` 3-claim collapse, migrate.py swallows decision-header parse failures, parse-one-file boundary leaking. Triaged per handoff; Finding B ships this cycle, Finding A proposal drafts for spec-review, Finding C's ADR promotes to accepted-pending-scheduling.
- **Canon schema — polarity surface underspecified** — Codex review on `weakens_assumption` narrow proposal rejected narrow path. Holistic audit (reconcile polarity vocabulary + coupled audit/citation/phase-0 surfaces + canon-CI gap FR-0035) dispatched to context-repo session.
- **Context-repo pass-2 retrofit** — M1+M2 retrofit for atlas landed (`49c24df` in atlas repo; 107/107 tests). skillfoundry-valuation-context retrofit proposal filed; awaiting skillfoundry session pickup.

## Pending principal (people-or-money only)

- **Atlas runner restart** — `sudo systemctl restart atlas-runner.service` deploys P1 + S3-P2 gate. 46h frozen. One command. (URGENT in runtime/.handoff/)
- **LCI outreach decision** — 10 drafts at `drafted` since 2026-04-11 (22+ days). Channel decision required: Tally form + outreach method, or explicit park/kill. URGENT in INBOX 37h.
- **Synaplex cap policy** — ADR-0029 §6 doc/code diverge (per-day vs per-fetch). Principal decision needed: truncate-by-score, truncate-by-recency, or ratify per-fetch + amend ADR. URGENT in INBOX 50h.
- **Tier-B-auto authority** — 14 cycles × 0 proposals landed. Approving autonomous Tier-B writes for additive, 2+-cycle infrastructure-only changes unblocks reflect.sh fix + 5+ stale proposals. Alternative: 30-min attended INBOX triage.

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
