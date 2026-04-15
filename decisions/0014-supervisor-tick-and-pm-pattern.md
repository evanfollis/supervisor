# ADR-0014: Hourly-class supervisor tick + project-manager tick pattern

Date: 2026-04-15
Status: accepted
Review: `/opt/workspace/runtime/.meta/adr-review-0014-2026-04-15T03-44-06Z.md`
  (Codex, "Accept with changes" — 7 concerns addressed below)

## Context

The supervisor is idle between attended `general` sessions. Handoffs
age in the INBOX, elephants sit unraised, project-side items stall
waiting for the next attended tick. The 12h reflection loop surfaces
*findings* but does not *do* anything with them. Principal directive
(2026-04-15): "Let's setup an hourly timer that spins you up and you
get to work moving forward with your to dos and assigning tasks to the
project managers… You should be improving [the PMs] so that you can
move up the stack."

ADR-0013 already established that reflection is first-class and that
friction compounds into system improvement. The missing piece is a
*driver* — a scheduled, headless supervisor session that processes
queued work, routes it to the right PM, reflects, and exits. Attended
`general` sessions remain the place where load-bearing decisions get
made; the tick is the between-session janitor and router.

The principal's stated cadence was hourly. That risks:
- Token cost on the order of ~170 headless sessions/week.
- Race conditions with attended `general` sessions (two Claude
  processes clobbering the same repo state).
- Drift amplification: many small autonomous commits accumulate
  without attended review.

The counter-argument to slowing the cadence is that friction goes
stale quickly and the point of the tick is freshness. A 2h cadence
still gives 12 opportunities per day to surface and route — far more
than the current 0 — and costs ~1/6th of hourly.

## Decision

### Cadence

- **`workspace-supervisor-tick.timer`** fires every 2h at **:47 past**
  the hour (00:47, 02:47, …, 22:47 UTC).
- Rationale for 2h: a tick run is expected to spend 2–5 minutes
  (read INBOX + run doctor + at most 2–3 routed handoffs + reflect).
  2h is ≫ duration (no spillover risk), offset by ≥24 min from both
  12h jobs (`reflect.timer` at :17, `synthesize.timer` at :23), and
  leaves the `:00` of the hour free for cron-class hygiene jobs the
  workspace may add later. :47 was chosen as the largest clean offset
  from both 12h slots without colliding with `:00`/`:30`.
- Cost envelope: ~12 ticks/day × ~5 min × Sonnet-default ≈ 30%–40%
  of the existing reflection+synthesis daily spend. Acceptable
  because most ticks will skip (attended-session overlap or empty
  INBOX).
- Cadence can be tightened or loosened by editing the unit file;
  changes require an ADR amendment with a cost/benefit note.

### Interlock (addresses review issue 1)

A tick must **not** race an attended supervisor session. The earlier
draft relied on Claude JSONL mtime alone; Codex review flagged three
gaps: Codex supervisor sessions have a different transcript store,
quiet-but-attended sessions have no recent JSONL write, and long
single tool-calls can silently exceed the 15-min window. The final
interlock stacks four independent signals and skips if **any** fires:

1. **Self-race** — `flock -n /opt/workspace/runtime/.locks/supervisor-tick.lock`
   at the top of the tick script. If held, exit 0.
2. **Claude JSONL freshness** — any
   `/root/.claude/projects/-opt-workspace-supervisor/*.jsonl`
   modified in the last 15 min → skip.
3. **Codex JSONL freshness** — any
   `/root/.codex/sessions/**/rollout-*.jsonl` whose containing
   session metadata shows `cwd=/opt/workspace/supervisor` and was
   modified in the last 15 min → skip. (Simpler heuristic if metadata
   lookup is brittle: any file under `/root/.codex/sessions/`
   touched in the last 15 min whose path or contents reference the
   supervisor cwd → skip. The tick script commits to the stricter
   check and falls back to the broader one on parse failure.)
4. **Tmux attended-session signal** — if
   `tmux display-message -p -t general '#{session_activity}'` returns
   an epoch within the last 15 min → skip. Captures cases where the
   attended agent is mid-tool-call and no transcript has flushed yet
   but the pane is receiving output, and cases where the human is
   typing into the pane.
5. **Manual hold** — if
   `/opt/workspace/runtime/.locks/supervisor-tick.hold` exists, exit
   immediately. Principal or attended agent drops this to suspend
   ticks without `systemctl disable`.

If any of 2–5 trips, the tick **still writes** a minimal report to
`/opt/workspace/runtime/.meta/supervisor-tick-<iso>.md` (one line:
`# Tick skipped — reason: <...>`) and appends a `session_reflected`
event with `"note":"tick skipped — <reason>"`. Skipped runs must be
visible — see "Failure observability" below (review issue 6).

Residual race the stack does **not** catch: an attended session that
is quiet for ≥15 min across all four signals simultaneously (no pane
activity, no transcript flush, no process observable via tmux). This
window exists. The mitigation is that the tick's own file writes are
preceded by a final `git status --porcelain` snapshot; if the diff
shows changes the tick did not author, the tick aborts and drops an
`URGENT-tick-unexpected-state.md` handoff for attended review.

### Scope — tiered writable surfaces (addresses review issue 5)

Codex review flagged that the initial "allow anything except charter"
model was both too loose (playbooks, system/*.md can reshape operator
behavior) and too tight (tick can't patch the playbook that would
encode the fix it just observed). The final model defines three
tiers:

**Tier A — tick may write freely**:
- `friction/FR-NNNN-*.md` (new records)
- `handoffs/INBOX/<iso>-*.md` (new entries, including
  `URGENT-*.md` for escalations)
- `handoffs/ARCHIVE/YYYY-MM/` (moving processed INBOX entries)
- `events/supervisor-events.jsonl` (append only)
- `system/status.md`, `system/active-issues.md`,
  `system/active-ideas.md` — operational state, tick may edit
- `/opt/workspace/runtime/.meta/supervisor-tick-<iso>.md` (its own
  report)
- `/opt/workspace/runtime/.handoff/<project>-*.md` (routing to PMs)
- `/opt/workspace/runtime/.meta/friction-promotion-queue.md`
  (informal work queue, tick-owned)

**Tier B — tick may propose, not commit**:
- `playbooks/*.md` — tick may write a draft to
  `handoffs/INBOX/playbook-update-<slug>.md` describing the change
  it wants, but may not edit the playbook directly. Attended session
  reviews and applies.
- `decisions/NNNN-*.md` drafts — tick may create ADRs in
  `Status: proposed` only; never `accepted`. An attended or
  cross-agent-reviewed session is required for acceptance.
- `ideas/IDEA-NNNN-*.json` — tick may create in `state: framed` only;
  state transitions require attended session.

**Tier C — forbidden to the tick**:
- `AGENT.md`, `CLAUDE.md`, `AGENTS.md` (charter)
- `/opt/workspace/CLAUDE.md` (workspace charter)
- `decisions/NNNN-*.md` — any edit to an existing file regardless of
  status (ADRs are immutable once written; corrections go in a new
  ADR)
- `scripts/lib/**`, `workspace.sh`, `systemd/**`, `config/**` — the
  tick cannot rewrite its own guardrails or infrastructure
- Anything under `/opt/workspace/projects/**` — project repos are
  never touched by the tick; cross-repo work is routed via handoff

### Scope — side effects (addresses review issue 2)

The earlier draft relied on a post-run `git status` diff. Codex
review correctly flagged that this misses: network calls, commits
in project repos, systemctl changes, writes outside the repo, and
write-then-revert. The tick enforces boundaries via **four layers**,
not one:

1. **OS-level filesystem sandbox** (strongest). The systemd service
   declares `ProtectSystem=strict`, `ProtectHome=read-only`, and
   `ReadWritePaths=` listing exactly the Tier A directories plus the
   supervisor `.git`. All other paths are read-only at the kernel
   level. Writes outside Tier A *cannot happen*, regardless of what
   the model decides to do. Network is *not* restricted — push to
   origin requires it — but HTTPS egress to anything other than
   github.com is not currently blocked at the OS level (tracked as
   follow-up: egress policy via a resolved-hosts allowlist).
2. **Claude CLI `--disallowedTools`** blocks `Bash(systemctl:*)`,
   `Bash(git -C /opt/workspace/projects*:*)`,
   `Bash(docker:*)`, `Bash(rm:*)`, `Bash(mv:*)`, `NotebookEdit`,
   and `Edit` patterns targeting Tier C paths (where the CLI
   supports path globs).
3. **Prompt-level declaration** of the three tiers so the model
   understands the intent, not just the walls.
4. **Post-run state audit**:
   - `git -C /opt/workspace/supervisor status --porcelain` filtered
     against Tier-C glob list — any hit aborts the tick and drops
     `handoffs/INBOX/URGENT-tick-boundary-breach-<iso>.md`.
   - `git -C /opt/workspace/projects/<each> rev-parse HEAD` compared
     to pre-run values — any change is a critical failure.
   - `systemctl daemon-reload --quiet 2>&1` — any stderr suggesting
     unit-file drift flags for investigation.

Write-then-revert is still possible inside Tier A (tick could write,
read, revert, and no diff remains). For Tier A this is fine — those
surfaces are tick-writable by design. For Tier C, the OS-level
read-only mount makes it structurally impossible.

### Push discipline (addresses review issue 3)

Codex review correctly flagged that the earlier draft's gates
(doctor-green + boundary-passed + supervisor-only-paths) prove
*hygiene*, not *correctness*. A tick can commit a wrong ADR draft,
noisy friction record, or misleading report and push it straight to
`main`. Recovery was unstated.

The final rule is stricter: **the tick never pushes.**

- Tick commits are made locally on branch `ticks/<date>-<hour>`
  (e.g., `ticks/2026-04-15-14`), not `main`. Branch name includes
  the hour so multiple ticks in a day produce separate branches.
- Commit trailers use `session_id: tick-<iso>` and `agent: tick` so
  tick-origin commits are greppable and visually distinct from
  attended commits.
- The next attended `general` session is responsible for reviewing
  `ticks/*` branches and either merging (fast-forward into `main`
  + push) or deleting. The attended session **must** do this as
  part of reentry; a standing check in `workspace.sh doctor` flags
  any tick branch older than 24h as a WARN and older than 72h as
  FAIL.
- If the attended session merges and a bad commit reaches `main`,
  recovery is `git revert <sha>` on an attended branch — standard
  git recovery, not a special case.

This is more conservative than the earlier draft deliberately: an
unattended headless agent should not write to shared `main` without
a human or opposing-agent review in the loop. Push speed is traded
for safety.

### Project-manager tick pattern — deferred (addresses review issue 4)

The earlier draft declared a per-project tick pattern in parallel
with the supervisor tick. Codex review correctly flagged this as a
separate design problem: per-project ticks assume each project has
the same transcript model, a friction surface, a safe event surface,
and a meaningful "recent reflection artifact" metric — none of which
hold uniformly today. The existing per-project `reflect.sh` is
deliberately read-only/propose-only; a write-capable project tick is
materially different and riskier.

The PM-improvement goal is preserved by a **lighter-weight initial
approach**, with the full per-project tick design deferred to a
follow-up ADR once the supervisor tick has demonstrated the shape:

1. **Playbook only** — `playbooks/project-tick-pattern.md` exists
   but describes discipline, not infrastructure: what a project
   session should do at the end of a session, how to emit a
   reflection artifact, how to declare friction, how to escalate
   cross-cutting items to supervisor's INBOX. No per-project timer
   is shipped in this ADR.
2. **Supervisor-driven grading** — each supervisor tick reads the
   most recent reflection artifact for each project under
   `/opt/workspace/runtime/.meta/<project>-reflection-*.md`. If the
   artifact is older than 48h *and* the project's git log shows
   activity in the same window, the supervisor tick writes a
   handoff to that project session: "your reflection loop is
   stale." This uses existing infrastructure (the 12h reflect
   timer) rather than new per-project ticks.
3. **Follow-up ADR** (queued, not this ADR): if the grading loop
   shows the playbook-only approach isn't enough to drive PM
   improvement, a subsequent ADR will ship per-project ticks with a
   fuller design — distinct from both `reflect.sh` and this
   supervisor tick, tailored to each project's substrate.

## Consequences

**Positive**

- Supervisor becomes proactive between attended sessions; elephants
  get surfaced without principal prompting (closes the structural
  half of FR-0007).
- Handoffs stop aging invisibly (addresses the SLA gap the new
  `doctor` check exposes).
- Project managers get a standing improvement loop, not just the
  existing 12h passive reflection. The supervisor is in a position
  to grade + nudge.
- Principal can step further up the stack: the system chases its
  own backlog.

**Negative / costs**

- Token spend: ~12 headless sessions/day for the supervisor alone.
  Mitigated by Sonnet-as-default and by the attended-race skip that
  often reduces actual runs.
- Failure mode if the boundary post-check is buggy: tick could
  mutate forbidden paths before the check fires. Mitigated by the
  check being "first thing after the claude process exits" and by
  the forbidden list being short and literal.
- Drift: many small tick commits fill the git log. Mitigated by the
  `tick-` trailer making them greppable, and by the 12h synthesis
  reading tick reports directly.

**Mitigations**

- `workspace.sh doctor` gains three tick-specific checks
  (addresses review issue 6 — failure observability):
  1. `workspace-supervisor-tick.timer` is active + enabled
  2. Most recent `supervisor-tick-*.md` report (including skipped
     runs, which also write a report) is not older than 4h when the
     timer is enabled. A skipped-every-run failure becomes visible
     because skipped runs emit reports too.
  3. Any `ticks/*` branch older than 24h = WARN, older than 72h =
     FAIL (forces attended review cadence).
- The 12h supervisor meta-reflection reads `supervisor-tick-*.md`
  artifacts and surfaces patterns across ticks — e.g., if every
  tick for 48h has produced low-quality output or repeatedly
  skipped for the same reason.
- A manual hold file (`.locks/supervisor-tick.hold`) gives any agent
  a graceful way to suspend the tick during sensitive work.
- Biggest-risk mitigation (Codex review): the ADR acknowledges that
  the honor-system failure mode is "we mistake 'no diff' for 'the
  tick respected the charter.'" The OS-level sandbox is the
  structural fix — filesystem writes outside Tier A cannot happen
  regardless of what the model decides, which is a categorical
  improvement over the honor-system pattern ADR-0013 is explicitly
  moving away from.

## Alternatives considered

- **Hourly cadence** (principal's initial ask): rejected in favor of
  2h for cost + race-risk reasons. Principal agreed.
- **Cron instead of systemd timer**: rejected; systemd gives us
  `Persistent=true`, cleaner logging via journalctl, and
  consistency with the rest of the workspace.
- **On-demand only (no schedule)**: rejected; leaves the supervisor
  idle between attended sessions, which is exactly the gap we're
  closing.
- **Supervisor tick also executes project-side work directly**:
  rejected; violates the charter boundary (`AGENT.md` §Boundaries).
  Tick routes via handoff; PM session executes.
- **No post-run boundary check, trust the prompt**: rejected;
  ADR-0013 and FR-0006/0007 all show that honor-system rules erode.
  Mechanical check is the fix-class, not the fix-instance.

## Follow-through

- [ ] `scripts/lib/supervisor-tick.sh` + `scripts/lib/supervisor-tick-prompt.md` shipped
- [ ] `systemd/workspace-supervisor-tick.service` + `.timer` installed and enabled, with OS-level sandbox hardening (`ProtectSystem=strict`, `ReadWritePaths=` Tier A only)
- [ ] `playbooks/supervisor-tick.md` written (procedure reference)
- [ ] `playbooks/project-tick-pattern.md` written (discipline template; no per-project timer)
- [ ] `workspace.sh doctor` gains tick-timer, tick-freshness (incl. skipped), and tick-branch-age checks
- [ ] Codex review artifact referenced in header:
      `/opt/workspace/runtime/.meta/adr-review-0014-2026-04-15T03-44-06Z.md`
- [ ] First real tick run verified manually by triggering the service
      once before enabling the timer
- [ ] Egress allowlist (systemd IPAddressAllow / resolved hosts) for
      push-to-github.com only — noted as follow-up, not blocking
