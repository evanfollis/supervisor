---
name: Active issues
description: Currently-live pressure on the workspace. Each entry is ≤3 lines. Historical / closed items live in `active-issues-archive.md`. Read this; load the archive on demand only.
updated: 2026-05-04
---

# Active issues

## Critical (action required)

- **Atlas runner frozen 42h+ (P1)** — `atlas-runner.service` not restarted since ~May 2. Evidence store stuck at 239. 22 signals/cycle, 0 hypotheses evaluated. Fix: `sudo systemctl restart atlas-runner.service`. URGENT filed; awaiting attended session with operator access.
- **reflect.sh Write bypass — cycle 10** — `reflect.sh:112` is missing `"Write"` in `--disallowedTools`, allowing reflection sessions to overwrite project files including CURRENT_STATE.md outside their mandate. One-line fix; URGENT filed (`URGENT-reflect-sh-write-bypass-2026-05-03T15-23Z.md`). 10 cycles without landing.
- **LATEST_SYNTHESIS pointer corruption** — `runtime/.meta/LATEST_SYNTHESIS` is a stale symlink pointing to Apr 29 synthesis; `synthesize.sh` writes through it, destroying historical content and leaving garbage for the executive dispatch gate. Fix: replace symlink write with `printf '%s\n' "$OUTPUT_FILE" > "$META_DIR/LATEST_SYNTHESIS"` in `synthesize.sh`.
- **Ghost-write telemetry corruption** — Tick sessions operate on tick branches but emit `session_reflected` events claiming changes "on main." Two ticks claimed to write FR-0038 and update active-issues on main; neither is present on main. `events.jsonl` is the charter-designated truth source; false entries degrade it. Requires tick telemetry to include a `branch` field (Proposal 1, synthesis 2026-05-04T03:26Z).
- **INBOX proposal saturation (39+ items, 6+ days)** — 39 Tier-B/C proposals in INBOX without disposition; URGENT filed 2026-04-28. 0/25 proposals have landed across 16 synthesis cycles. Saturation exception active. Terminal consumer bottleneck — requires attended principal session for bulk disposition.

## Currently live (project work)

- **Command browser-layer verification** — server-side smoke is strong, but real-browser coverage remains a machine-owned gap. Old principal FR-0015 escalation archived; replacement handoff is `runtime/.handoff/command-browser-verification-owned-2026-04-25T1310Z.md`.
- **Synaplex site V1 deploy to synaplex.ai** — site scaffold builds clean at `projects/synaplex/site/dist/`; rebrand landed; deploy still pending. IA reshape decision open (§Open design questions in ADR-0027). Dispatched to synaplex session.
- **Synaplex loop L2/L3/L4 subsystems** — L1 intake live; Layer 2 reasoning (per-beat candidate emission), Layer 3 validation (counter-search + nightly integrity), Layer 4 presentation (writeups → site + newsletter) follow ADR-0029's bootstrap throttle (≤5 candidates/beat/day for 4 weeks).
- **Synaplex cap policy decision needed** — ADR-0029 §6 says "max 200 per source per day"; implementation does "max 200 per fetch." HN reaching ~400/day. Options: A) truncate post-merge by score, B) by recency, C) ratify per-fetch semantic + amend ADR-0029. URGENT filed. Principal decision required.
- **Skillfoundry agentic inbound deploy** — Preflight landing route + `sourceType` + watcher restart; Launchpad Lint + LCI landing + telemetry; ≥1 blog post/probe/week. In flight per the skillfoundry session.
- **LCI outreach blocked 22+ days** — 10 drafts at `drafted` status since 2026-04-11. Zero external evidence for LCI commercial assumption. URGENT filed. Requires principal decision: unblock (channel + Tally form), park explicitly with ADR, or kill lane.
- **Discovery adapter post-fix findings** — 3 new findings from Codex review on `2f63ae5`: `parse_assumption` 3-claim collapse, migrate.py swallows decision-header parse failures, parse-one-file boundary leaking. Triaged per handoff; Finding B ships this cycle, Finding A proposal drafts for spec-review, Finding C's ADR promotes to accepted-pending-scheduling.
- **Canon schema — polarity surface underspecified** — Codex review on `weakens_assumption` narrow proposal rejected narrow path. Holistic audit (reconcile polarity vocabulary + coupled audit/citation/phase-0 surfaces + canon-CI gap FR-0035) dispatched to context-repo session.
- **Context-repo pass-2 retrofit** — M1+M2 retrofit for atlas landed (`49c24df` in atlas repo; 107/107 tests). skillfoundry-valuation-context retrofit proposal filed; awaiting skillfoundry session pickup.

## Pending principal (people-or-money only)

- **LCI lane decision** — see LCI item above. One of: unblock (channel decision), park (ADR), or kill.
- **Synaplex cap policy** — see synaplex cap item above. One of: A/B/C disposition.
- **Tier-B-auto authority** — 16 cycles, 0/25 proposals landed. Should ticks be authorized to implement additive changes to `supervisor/scripts/lib/` (reflect.sh Write fix, LATEST_SYNTHESIS pointer fix, rotation-blind telemetry fix)? This single decision unblocks ~8 standing proposals. Options: authorize for listed scripts only, or continue requiring attended session for all script changes.

## Structural / background

- **Tick branch merge overdue** — 9 branches aged >72h (✗); 21 more >24h (⚠). All governance writes on tick branches (FR-0038 claims, active-issues updates) are ghost-writes until merged. Doctor FAIL. Attended session needed to merge or prune.
- **Rotation-blind reflection telemetry** — reflection jobs running at 02:xx UTC miss ~10h of prior-day events due to log rotation. Fix: `zcat` most recent archive before filtering. Affects every project at 02:xx cycle (Proposal 3, synthesis 2026-05-04T03:26Z).
- **Operator authority loop** — attached sessions can be executive/supervisor with repo write but no tmux/systemd host control. ADR-0015 amendment now forbids routing Evan to another "full admin" agent; repeated host-only needs must become an explicit operator bridge/tool.
- **Executive boundary discipline** — FR-0018 and follow-ons name the pattern where the executive session patches project code instead of shaping the PM layer. Ongoing; reinforced by ADR-0020 action-default + the people-or-money rubric memory.
- **ADR-0028 post-landing artifact hygiene** — artifact inbox still needs owned browser-layer proof before retiring the old `/_inbox` stopgap. Do not ask the principal for the proof path by default.
- **Workspace CLAUDE.md versioned as of `d09d2be`** — symlink from `/opt/workspace/CLAUDE.md` → `supervisor/workspace-claude.md`. All future workspace-charter edits land in git history via the supervisor repo.
- **Cowork is a secondary friction surface** — external commentary only; not a gate, validator, or backlog priority escalator. Durable contract: ADR-0032.

---

Archive for closed items: `system/active-issues-archive.md` (not auto-loaded).
