---
name: Active issues
description: Currently-live pressure on the workspace. Each entry is ≤3 lines. Historical / closed items live in `active-issues-archive.md`. Read this; load the archive on demand only.
updated: 2026-07-11T22:42Z
---

# Active issues

Rewritten from live sources during the attended session of 2026-07-11
(ADR-0037). Prior snapshot (2026-06-09, 32 days stale) is in the archive.
Cross-check any claim here against `runtime/.meta/LATEST_SYNTHESIS` first.

## CRITICAL / time-critical

_(none as of 2026-07-11T23:15Z)_

- ~~Atlas Phase 2b~~ **CLOSED 2026-07-11T23:05Z** — scorer shipped +
  deployed (`cf76b7b`, 184 tests, runner restarted 22:51Z); bucket 2948
  recovered (20 scored), 2949 self-scores on Jul 16. Follow-on: 2c
  calibration CLI (not time-critical).
- ~~Unpushed branches~~ **CLOSED 2026-07-11T23:10Z** — principal authorized;
  supervisor/context-repository/command/skillfoundry-harness pushed after
  audit (composition + secrets scan, 0 hits); atlas + sf-products already in
  sync. **Exception: synaplex has NO git remote** — "push synaplex" (rec
  #19) was never executable; creating the GitHub repo is a principal-facing
  naming/visibility decision.

## Currently live (verified 2026-07-11)

- **Tick recovery verification** — dirty-tree deadlock fixed 2026-07-11
  (events ledger excluded from gate, commit `0ef69f2`). First post-fix tick
  ~2026-07-11T22:47Z; confirm a `supervisor-tick-*.md` shows a real run, then
  delete `handoffs/INBOX/URGENT-tick-escalation-9c6d9d393b.md`.
- **INBOX saturation — 333 items** — mostly duplicate synthesis-translator
  proposals (P3a suppression enforcement never landed). Sweep + P3a fix
  pending.
- **Synthesis follow-ups still unlanded** — P3 (reflection failure
  self-reporting), P5 (reflect.sh HEAD-check false positive — source of the
  `URGENT-supervisor-reflection-mutated-head` noise), P3a (INBOX
  suppression), P2 (activity-gated reflection). All small `reflect.sh` /
  translator patches; see C138 for specs.
- **Hook injection hardening (ADR-0037 review findings)** — the
  session-start hook keys freshness on `updated:` only (not `generated:`)
  and does not escape inner code fences; both matter if any generated file
  is ever added to always-load. Deferred; do before any such addition.
- **always-load 30KB cap collision** — aggregate exceeds cap; injection
  truncates tail files (URGENT handoff `synaplex-always-load-cap-collision`
  to principal). This rewrite shrinks active-issues from 10.3KB to ~4KB but
  does not close it.
- **ANTHROPIC_API_KEY for synaplex intake prose synthesis** — heuristic
  fallback active 61+ cycles; needs principal-provisioned credential at
  `runtime/.secrets/`. Intake itself is healthy (W27 current, W28 due
  Jul 12).
- ~~atlas-runner restart~~ **CLOSED** — restarted 2026-07-11T22:51Z with the
  Phase 2b deploy; picked up `f24d298`.
- **Codex config migrated 2026-07-11** — legacy `profile = "full_auto"`
  rejected by the current codex CLI (breakage is recent: nightly maintenance
  still ran at 01:23Z Jul 11). Migrated to `full_auto.config.toml`; `codex
  exec` verified working post-migration. Watch tonight's 01:23Z run; backup
  at `/root/.codex/config.toml.bak-2026-07-11`.
- **Host reboot pending** — health snapshot 2026-07-11: `[REBOOT REQUIRED]`,
  14 upgradable packages, uptime 4w3d. Principal-facing (restarts all
  sessions).

## Carried, unverified since 2026-06-09 (see archive for detail)

- Synaplex site V1 deploy to synaplex.ai; L2/L3/L4 subsystems; cap policy
  doc/code divergence.
- Skillfoundry agentic inbound deploy; LCI outreach channel decision
  (principal); discovery-adapter findings A/C.
- Canon polarity audit (context-repo); pass-2 retrofit pickup.
- Command browser-layer verification gap.
- `synthesis_reviewed` event regression (C57 P1); reflection accuracy gap
  (reads CURRENT_STATE.md instead of live sources).
