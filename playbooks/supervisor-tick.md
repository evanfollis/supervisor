# Playbook: Supervisor tick

**Trigger**: `workspace-supervisor-tick.timer` every 2h at :47 past.
Also runnable manually:
`/opt/workspace/supervisor/scripts/lib/supervisor-tick.sh`.

**Owner**: the tick itself (autonomous). Attended sessions supervise
and merge.

**Preconditions (interlock stack)**:
1. No other tick running (flock on
   `/opt/workspace/runtime/.locks/supervisor-tick.lock`).
2. No manual hold file at
   `/opt/workspace/runtime/.locks/supervisor-tick.hold`.
3. No Claude supervisor JSONL activity in last 15 min.
4. No Codex session referencing `/opt/workspace/supervisor` cwd in
   last 15 min.
5. Tmux `general` session `session_activity` older than 15 min.
6. Supervisor repo working tree is clean (no uncommitted changes).

If any precondition trips, the tick writes a minimal
`runtime/.meta/supervisor-tick-<iso>.md` stating the skip reason,
emits a `session_reflected` event, and exits 0.

**Outputs (when not skipped)**:
- A detailed report at
  `/opt/workspace/runtime/.meta/supervisor-tick-<iso>.md`
- Possibly new `friction/FR-NNNN-*.md`, new
  `handoffs/INBOX/<iso>-*.md`, updates to `system/*.md`, moved
  `handoffs/ARCHIVE/`
- Possibly new handoffs to project sessions under
  `/opt/workspace/runtime/.handoff/<project>-*.md`
- A tick commit on `ticks/<YYYY-MM-DD>-<HH>` branch (never on main,
  never pushed)
- Appended events on `events/supervisor-events.jsonl` including
  `session_reflected` at end

## What the tick does

See ADR-0014 for the full contract. Short form:

1. Checks all interlocks; skips if any fire.
2. Reads current-state bundle (`system/*.md`, INBOX, recent synthesis,
   recent events).
3. Processes INBOX — routes pure-routing items to PM sessions via
   `/opt/workspace/runtime/.handoff/`, archives them.
4. Age-checks existing INBOX; escalates anything older than 24h.
5. Runs `workspace.sh doctor`; files URGENT handoffs if FAIL.
6. Grades PM reflection freshness; nudges stale ones via handoff.
7. Routes synthesis proposals not yet tracked.
8. Harvests friction signals (FR-NNNN).
9. Writes the report.
10. Commits Tier-A writes to `ticks/<date>-<hour>`; rewinds main.

## What an attended general session does to close the loop

Every attended `general` session must, on reentry, handle ticks/*
branches as part of its session-start sweep. `workspace.sh doctor`
will warn at 24h and fail at 72h to force this cadence.

### Reentry sweep for ticks/* branches

```bash
# 1. List tick branches
git -C /opt/workspace/supervisor branch --list 'ticks/*' --sort=-committerdate

# 2. For each, inspect the commits
git -C /opt/workspace/supervisor log main..ticks/<date>-<hour> --stat

# 3. Decision:
#    - Good tick work → merge fast-forward or cherry-pick into main, then push
#    - Mixed (some good, some noisy) → cherry-pick the good commits, delete
#      the branch, write an INBOX note for the deferred items
#    - Bad → delete the branch, note in INBOX / friction if the pattern
#      repeats across ticks
```

Delete merged tick branches promptly. They are not durable; the
content they carried lives on main once merged.

### What to watch for when reviewing a tick

- **Boundary breach**: if the tick produced an
  `URGENT-tick-boundary-breach-*.md`, investigate before doing
  anything else. `--disallowedTools` or the OS-level sandbox may
  need tightening.
- **Noisy friction**: the tick over-captures if friction files are
  duplicative or low-signal. Tune the prompt.
- **Stuck routing**: if the same INBOX item shows up multiple ticks
  in a row without movement, it is attended-only — the tick keeps
  deferring. Resolve it in the attended session.
- **PM grading misfires**: if the tick keeps nudging a PM whose
  reflection is current, the grading heuristic is wrong. Fix in
  the prompt or the reflection-file conventions.

## Suspending the tick

To suspend for sensitive work:

```bash
touch /opt/workspace/runtime/.locks/supervisor-tick.hold
```

To resume:

```bash
rm /opt/workspace/runtime/.locks/supervisor-tick.hold
```

Prefer the hold file over `systemctl disable` — it is observable in
the tick reports and self-documenting.

## Anti-patterns

- **Merging ticks branches without reviewing commits.** A tick
  commits on autonomous judgment; the merge is the review gate.
  Skipping review defeats the design.
- **Letting tick branches accumulate.** Each one is dead weight
  until merged or deleted. Doctor's 24h/72h checks exist to force
  the sweep.
- **Editing the tick script or prompt mid-attended-session without
  an ADR amendment.** The tick's guardrails are load-bearing; they
  need explicit governance, not ad hoc tweaks.
- **Treating tick-authored friction as low-quality by default.** It
  often catches patterns the attended session is too close to see.
